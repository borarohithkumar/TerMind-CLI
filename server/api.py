"""
TerMind Core API Server
Architecture: FastAPI REST endpoint integrating a Hybrid NLP-to-Bash Engine.
Models: SentenceTransformer (all-mpnet-base-v2) + FAISS Vector Index + T5-Base (Fallback).
"""

from fastapi import FastAPI
from pydantic import BaseModel
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Initialize the REST API
app = FastAPI(
    title="TerMind Engine API", 
    description="Microservice for translating natural language to Linux system commands.",
    version="3.0"
)

print("System: Booting Machine Learning Models...")

# 1. Load the Semantic Search Infrastructure (Primary Path)
st_model = SentenceTransformer('all-mpnet-base-v2')
index = faiss.read_index('data/faiss_index.bin')
with open('data/commands_mapping.json', 'r') as f:
    faiss_commands = json.load(f)

# 2. Load the Generative Transformer (Fallback Path)
tokenizer = T5Tokenizer.from_pretrained("t5-base", legacy=False)
t5_model = T5ForConditionalGeneration.from_pretrained("t5-base")

print("System: AI Models loaded. Listening for requests.")

class QueryRequest(BaseModel):
    """Data schema for incoming HTTP POST requests."""
    query: str

@app.post("/translate")
async def translate_query(request: QueryRequest):
    """
    Main routing logic. 
    Attempts high-speed FAISS vector retrieval first. If the semantic distance 
    exceeds the confidence threshold, routes the query to the T5 generative model.
    """
    # --- PATH A: FAISS RETRIEVAL ---
    # Convert incoming text to a 768-dimensional tensor array
    query_vector = st_model.encode([request.query])
    
    # Search the pre-computed L2 index for the nearest neighbor
    distances, indices = index.search(np.array(query_vector).astype('float32'), k=1)
    faiss_score = float(distances[0][0])
    faiss_cmd = faiss_commands[indices[0][0]]

    # --- PATH B: T5 GENERATION ---
    # Construct context-aware prompt for the T5 model
    input_ids = tokenizer.encode(f"translate English to Bash command: {request.query}", return_tensors="pt", max_length=96, truncation=True)
    outputs = t5_model.generate(input_ids, max_length=48)
    t5_cmd = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # --- HYBRID ROUTING PIPELINE ---
    CONFIDENCE_THRESHOLD = 1.0 
    
    if faiss_score < CONFIDENCE_THRESHOLD:
        final_cmd = faiss_cmd
        logic = "FAISS Semantic Match (High Confidence)"
    else:
        final_cmd = t5_cmd
        logic = "T5 Generative Fallback (Novel Query)"

    return {
        "query": request.query,
        "final_command": final_cmd,
        "logic_used": logic,
        "faiss_distance_score": faiss_score
    }
