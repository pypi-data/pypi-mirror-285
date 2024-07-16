import os
import subprocess
import logging
from huggingface_hub import snapshot_download

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_model_files(repo_id, local_dir):
    if not os.path.isdir(local_dir) or not os.path.isfile(f"{local_dir}/config.json"):
        logging.info(f"Model files not found locally. Downloading from {repo_id} to {local_dir}")
        snapshot_download(repo_id=repo_id, local_dir=local_dir, local_dir_use_symlinks=False)
    else:
        logging.info(f"Model files found locally at {local_dir}")

def create_directory(dir_path):
    os.makedirs(dir_path, exist_ok=True)

def quantize(model, outbase, outdir, llama_cpp_dir, quant_types, remove_fp16):
    if not os.path.isdir(model):
        raise FileNotFoundError(f"Could not find model dir at {model}")
    if not os.path.isfile(f"{model}/config.json"):
        raise FileNotFoundError(f"Could not find config.json in {model}")

    create_directory(outdir)
    fp16 = f"{outdir}/{outbase}.fp16.gguf"

    logging.info(f"Making unquantized GGUF at {fp16}")
    if not os.path.isfile(fp16):
        subprocess.run(f"python {llama_cpp_dir}/convert_hf_to_gguf.py {model} --outtype f16 --outfile {fp16}", shell=True, check=True)
    else:
        logging.info(f"Unquantized GGUF already exists at: {fp16}")

    logging.info("Making quants")
    for q_type in quant_types:
        outfile = f"{outdir}/{outbase}.{q_type}.gguf"
        logging.info(f"Making {q_type} : {outfile}")
        subprocess.run(f"{llama_cpp_dir}/llama-quantize {fp16} {outfile} {q_type}", shell=True, check=True)

    if remove_fp16:
        os.remove(fp16)

def run_quantization(config):
    setup_logging()
    try:
        ensure_model_files(config.INPUT_DIR, config.LOCAL_MODEL_DIR)
        quantize(
            config.LOCAL_MODEL_DIR, 
            config.BASE_MODEL_NAME, 
            config.OUTPUT_DIR,
            config.LLAMA_CPP_DIR,
            config.QUANT_TYPES,
            config.REMOVE_FP16
        )
    except Exception as e:
        logging.error(f"Quantization failed: {e}")