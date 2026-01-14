import os
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments




PROMPT_TEMPLATE = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
### Instruction:
{question}
### Input:
{context}
### Response:
{answer}"""


def formatting_func(examples: dict) -> list[str]:
    questions = examples.get("question") or []
    contexts = examples.get("context") or []
    answers = examples.get("answer") or []

    out: list[str] = []
    for q, c, a in zip(questions, contexts, answers):
        question = (q or "").strip()
        context = (c or "").strip()
        answer = (a or "").strip()
        out.append(PROMPT_TEMPLATE.format(question=question, context=context, answer=answer))
    return out


def main() -> None:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/llama-3-8b-bnb-4bit",
        max_seq_length=2048,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )

    dataset = load_dataset("b-mc2/sql-create-context", split="train")

    output_dir = os.environ.get("OUTPUT_DIR", "outputs")

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=1,
        logging_steps=10,
        save_steps=200,
        save_total_limit=2,
        fp16=False,
        bf16=True,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        formatting_func=formatting_func,
        max_seq_length=2048,
        args=training_args,
    )

    trainer.train()

    model.save_pretrained("lora_adapters")
    tokenizer.save_pretrained("lora_adapters")


if __name__ == "__main__":
    main()
