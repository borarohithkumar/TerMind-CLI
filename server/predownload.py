"""
TerMind Model Pre-loader
Executes during the Docker build process to bake HuggingFace weights 
directly into the container image, ensuring zero-latency boot times in production.
"""

from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration

def bake_models():
    print("DevOps Pipeline: Fetching and baking ML models into container layer...")
    
    # 1. Semantic Search Model (FAISS Encodings)
    print("-> Downloading all-mpnet-base-v2...")
    SentenceTransformer('all-mpnet-base-v2')
    
    # 2. Generative Fallback Model (T5)
    print("-> Downloading t5-base tokenizer and weights...")
    T5Tokenizer.from_pretrained("t5-base", legacy=False)
    T5ForConditionalGeneration.from_pretrained("t5-base")
    
    print("✅ Models successfully cached into the Docker image!")

if __name__ == "__main__":
    bake_models()
