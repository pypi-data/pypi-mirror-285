from huggingface_hub import HfApi
import os


def upload_to_hf(files, output_dir, hf_repo_id, hf_api_token):
    api = HfApi()
    for file in files:
        file_path = os.path.join(output_dir, file)
        if os.path.exists(file_path):
            print(f"Uploading {file}")
            api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=file,
                repo_id=hf_repo_id,
                token=hf_api_token,
            )
        else:
            print(f"Warning: {file} not found in {output_dir}")
    print("Upload completed")
