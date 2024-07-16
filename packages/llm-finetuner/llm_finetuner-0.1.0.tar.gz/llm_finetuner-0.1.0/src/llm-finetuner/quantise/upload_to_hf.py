from huggingface_hub import HfApi
import os
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_to_hf(hf_repo_id, output_dir, base_model_name, quant_types, hf_token):
    if not hf_token:
        raise ValueError("Hugging Face token is not set. Please set the HF_TOKEN environment variable.")

    api = HfApi(token=hf_token)

    for q_type in quant_types:
        local_file_path = f'{output_dir}/{base_model_name}.{q_type}.gguf'
        file_name = os.path.basename(local_file_path)
        
        api.upload_file(
            path_or_fileobj=local_file_path,
            path_in_repo=file_name,
            repo_id=hf_repo_id,
            repo_type='model',
        )
        
        logging.info(f'Uploaded {file_name} to {hf_repo_id}')

def run_upload(config):
    setup_logging()
    try:
        upload_to_hf(
            config.HF_REPO_ID,
            config.OUTPUT_DIR,
            config.BASE_MODEL_NAME,
            config.QUANT_TYPES,
            config.HF_TOKEN
        )
    except Exception as e:
        logging.error(f"Upload failed: {e}")

