import os
import boto3
from transformers import TrainerCallback

class SaveModelCallback(TrainerCallback):
    def __init__(self, save_steps, output_dir, s3_bucket=None, s3_prefix=None):
        self.save_steps = save_steps
        self.output_dir = output_dir
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.s3_client = boto3.client('s3') if s3_bucket else None
        
    def on_step(self, args, state, control, **kwargs):
        if state.global_step % self.save_steps == 0:
            checkpoint_dir = os.path.join(self.output_dir, f"checkpoint-{state.global_step}")
            state.save_model(checkpoint_dir)

            if self.s3_client:
                s3_key = os.path.join(self.s3_prefix, f"checkpoint-{state.global_step}")
                self.s3_client.upload_file(checkpoint_dir, self.s3_bucket, s3_key)
                print(f"Model checkpoint uploaded to S3: {s3_key}")