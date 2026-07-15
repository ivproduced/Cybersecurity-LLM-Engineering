"""Configuration-driven LoRA training with validated automatic resume."""

from __future__ import annotations

import argparse
import inspect
from pathlib import Path
from typing import Any

from src.training.checkpoints import find_latest_valid_checkpoint, validate_checkpoint


def load_config(path: str | Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - exercised only without project deps
        raise RuntimeError("Install project dependencies with: pip install -e .") from exc
    with Path(path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("configuration root must be a mapping")
    for section in ("model", "data", "lora", "training"):
        if section not in config:
            raise ValueError(f"missing configuration section: {section}")
    return config


def resolve_resume(value: str | None, output_dir: str | Path) -> Path | None:
    """Resolve ``auto``, ``none``, or an explicit full-state checkpoint path."""
    if value is None or value.casefold() in {"none", "false", "off"}:
        return None
    if value.casefold() == "auto":
        return find_latest_valid_checkpoint(output_dir, full_state=True)
    checkpoint = Path(value).expanduser()
    problems = validate_checkpoint(checkpoint, full_state=True)
    if problems:
        raise ValueError(f"cannot resume from {checkpoint}: {'; '.join(problems)}")
    return checkpoint


def run_training(config: dict[str, Any]) -> Path:
    """Execute a Hugging Face PEFT training run and return the final adapter path."""
    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:  # pragma: no cover - requires optional GPU stack
        raise RuntimeError("Install the training stack with: pip install -e '.[training]'") from exc

    model_config = config["model"]
    data_config = config["data"]
    lora_config = config["lora"]
    train_config = config["training"]

    model_name = model_config["name"]
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, trust_remote_code=bool(model_config.get("trust_remote_code", False))
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype_name = str(model_config.get("dtype", "bfloat16"))
    dtype = getattr(torch, dtype_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        trust_remote_code=bool(model_config.get("trust_remote_code", False)),
    )
    if train_config.get("gradient_checkpointing", True):
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()
        model.config.use_cache = False

    adapter = LoraConfig(
        task_type="CAUSAL_LM",
        r=int(lora_config["rank"]),
        lora_alpha=int(lora_config["alpha"]),
        lora_dropout=float(lora_config.get("dropout", 0.0)),
        bias="none",
        target_modules=list(lora_config["target_modules"]),
    )
    model = get_peft_model(model, adapter)
    model.print_trainable_parameters()

    data_files = {"train": data_config["train_file"]}
    if data_config.get("validation_file"):
        data_files["validation"] = data_config["validation_file"]
    dataset = load_dataset("json", data_files=data_files)
    question_field = data_config.get("question_field", "question")
    answer_field = data_config.get("answer_field", "answer")

    def format_record(record: dict[str, Any]) -> dict[str, str]:
        messages = [
            {"role": "user", "content": str(record[question_field])},
            {"role": "assistant", "content": str(record[answer_field])},
        ]
        return {
            "text": tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
        }

    formatted = dataset.map(
        format_record,
        remove_columns=dataset["train"].column_names,
        desc="Formatting conversations",
    )
    max_length = int(data_config.get("max_sequence_length", 2048))

    def tokenize_batch(batch: dict[str, list[str]]) -> dict[str, Any]:
        return tokenizer(batch["text"], truncation=True, max_length=max_length, padding=False)

    tokenized = formatted.map(
        tokenize_batch,
        batched=True,
        remove_columns=["text"],
        desc="Tokenizing",
    )

    has_validation = "validation" in tokenized
    output_dir = Path(train_config["output_dir"])
    arguments = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=float(train_config.get("epochs", 1)),
        per_device_train_batch_size=int(train_config.get("per_device_train_batch_size", 2)),
        per_device_eval_batch_size=int(train_config.get("per_device_eval_batch_size", 2)),
        gradient_accumulation_steps=int(train_config.get("gradient_accumulation_steps", 4)),
        learning_rate=float(train_config.get("learning_rate", 2e-5)),
        lr_scheduler_type=str(train_config.get("lr_scheduler_type", "cosine")),
        warmup_ratio=float(train_config.get("warmup_ratio", 0.03)),
        weight_decay=float(train_config.get("weight_decay", 0.01)),
        max_grad_norm=float(train_config.get("max_grad_norm", 1.0)),
        bf16=dtype_name == "bfloat16",
        fp16=dtype_name == "float16",
        eval_strategy="steps" if has_validation else "no",
        eval_steps=int(train_config.get("eval_steps", 2000)),
        save_strategy="steps",
        save_steps=int(train_config.get("save_steps", 2000)),
        save_total_limit=int(train_config.get("save_total_limit", 5)),
        logging_steps=int(train_config.get("logging_steps", 100)),
        dataloader_num_workers=int(train_config.get("dataloader_num_workers", 4)),
        report_to=list(train_config.get("report_to", [])),
        seed=int(train_config.get("seed", 42)),
    )
    trainer_kwargs: dict[str, Any] = {
        "model": model,
        "args": arguments,
        "train_dataset": tokenized["train"],
        "eval_dataset": tokenized.get("validation"),
        "data_collator": DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    }
    if "processing_class" in inspect.signature(Trainer.__init__).parameters:
        trainer_kwargs["processing_class"] = tokenizer
    else:  # Backward compatibility with older Transformers releases.
        trainer_kwargs["tokenizer"] = tokenizer
    trainer = Trainer(**trainer_kwargs)

    checkpoint = resolve_resume(train_config.get("resume", "auto"), output_dir)
    trainer.train(resume_from_checkpoint=str(checkpoint) if checkpoint else None)

    final_path = output_dir / "final-adapter"
    trainer.save_model(str(final_path))
    tokenizer.save_pretrained(str(final_path))
    return final_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/example.yaml"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    final_path = run_training(load_config(args.config))
    print(f"Saved adapter to {final_path}")


if __name__ == "__main__":
    main()

