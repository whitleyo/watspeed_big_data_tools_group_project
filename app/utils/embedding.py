from app.utils.model_loader import download_s3_model, load_model
import torch
from sklearn.metrics.pairwise import cosine_similarity

MODEL_DIR = "./models/local_embedding"
BUCKET = "your-bucket-name"
PREFIX = "models/embedding_model"
USE_SENTENCE_TRANSFORMERS = False  # or True

download_s3_model(BUCKET, PREFIX, MODEL_DIR)
model, tokenizer = load_model(MODEL_DIR, use_sentence_transformers=USE_SENTENCE_TRANSFORMERS)

def embed(texts):
    if USE_SENTENCE_TRANSFORMERS:
        return model.encode(texts)
    else:
        with torch.no_grad():
            encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
            outputs = model(**encoded_input)
            return outputs.last_hidden_state.mean(dim=1).cpu().numpy()

def get_top_matches(query, corpus, top_k=5):
    query_emb = embed([query])
    corpus_emb = embed(corpus)
    scores = cosine_similarity(query_emb, corpus_emb).flatten()
    return scores.argsort()[-top_k:][::-1]

# TODO: Implement a function to run summarization given a query and found top matches
# This could involve loading a summarization model and processing the top matches.
# Maybe use Llama Instruct? Could also implement via a notebook