import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer
from .utils import SaveModelCallback


def train_model(base_model, new_model, dataset_name, lora_config, training_args, s3_config=None):
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=False,
    )

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False
    model.config.pretraining_tp = 1
    model.gradient_checkpointing_enable()
    
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    tokenizer.padding_side = 'right'
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_eos_token = True
    model = prepare_model_for_kbit_training(model)
    dataset = load_dataset(dataset_name, split="train")
    peft_config = LoraConfig(**lora_config)
    training_arguments = TrainingArguments(**training_args)

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="formatted_text",
        tokenizer=tokenizer,
        args=training_arguments,
        packing=False,
        callbacks=[SaveModelCallback(training_arguments.save_steps, training_arguments.output_dir, 
                                     s3_config['bucket'] if s3_config else None, 
                                     s3_config['prefix'] if s3_config else None)],
    )

    trainer.train()
    trainer.model.save_pretrained(new_model)
    return trainer

