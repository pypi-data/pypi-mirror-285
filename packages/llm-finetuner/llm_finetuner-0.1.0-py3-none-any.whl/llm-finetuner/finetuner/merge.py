import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import ModelCard, CardData, HfApi

def merge_model(base_model, new_model, hf_model_dir, hf_api_token):
    base_model_reload = AutoModelForCausalLM.from_pretrained(
        base_model,
        return_dict=True,
        low_cpu_mem_usage=True,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base_model_reload, new_model)
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    
    model = model.merge_and_unload()
    
    os.makedirs(hf_model_dir, exist_ok=True)
    model.save_pretrained(hf_model_dir)
    tokenizer.save_pretrained(hf_model_dir)

    card = ModelCard.from_template(
        CardData(
            language="en",
            license="apache-2.0",
            library_name="transformers",
            model_name=new_model,
            finetuned_from=base_model
        )
    )
    card.save(os.path.join(hf_model_dir, "README.md"))

    api = HfApi()
    api.upload_folder(
        folder_path=hf_model_dir,
        repo_id=new_model,
        repo_type="model",
        token=hf_api_token
    )

    return hf_model_dir