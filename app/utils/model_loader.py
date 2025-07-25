import os
import boto3
from transformers import AutoTokenizer, AutoModel, AutoConfig
from sentence_transformers import SentenceTransformer

def download_s3_model(bucket: str, prefix: str, dest_dir: str):
    s3 = boto3.client("s3")
    os.makedirs(dest_dir, exist_ok=True)
    files = ["config.json", "pytorch_model.bin", "tokenizer_config.json", "vocab.txt"]

    for fname in files:
        s3.download_file(bucket, f"{prefix}/{fname}", os.path.join(dest_dir, fname))

def load_model(local_dir: str, use_sentence_transformers=False):
    if use_sentence_transformers:
        return SentenceTransformer(local_dir), None
    else:
        tokenizer = AutoTokenizer.from_pretrained(local_dir)
        config = AutoConfig.from_pretrained(local_dir)
        model = AutoModel.from_pretrained(local_dir, config=config)
        model.eval()
        return model, tokenizer
