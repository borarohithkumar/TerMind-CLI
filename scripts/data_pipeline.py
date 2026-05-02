"""
TerMind Data Augmentation & Indexing Pipeline
Pulls verified NLP-to-Bash datasets from HuggingFace, executes semantic 
combinatorial augmentation, and compiles a 768-dimensional FAISS vector index.
"""

import json
import itertools
import numpy as np
import faiss
import time
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

def build_pipeline():
    start_time = time.time()
    
    # 1. Fetch Verified Baseline Data
    print("1. Fetching Verified High-Quality Bash Datasets...")
    real_data = []
    try:
        ds = load_dataset("westenfelder/NL2SH-ALFA", "train", split="train")
        for item in ds:
            if item.get("nl") and item.get("bash"):
                real_data.append({"nl": item["nl"], "cmd": item["bash"]})
        print(f"Successfully loaded {len(real_data)} real samples.")
    except Exception as e:
        print(f"Primary source error: {e}")

    # 2. Semantic Augmentation Matrix
    print("2. Executing Refined Semantic Augmentation...")
    semantic_groups = [
        {
            "cmds": ["ls -la", "tree -L 2", "lsblk -f", "ls -R"],
            "targets": ["files", "hidden files", "folder contents", "directory structure", "block devices"],
            "verbs": ["list", "show", "display", "view"]
        },
        {
            "cmds": ["df -hT", "du -ah --max-depth=1", "free -h"],
            "targets": ["disk space", "memory usage", "storage", "filesystem info", "free ram"],
            "verbs": ["check", "show", "report", "get"]
        },
        {
            "cmds": ["top -b -n 1", "ps aux --sort=-%mem", "uptime -p"],
            "targets": ["processes", "system status", "cpu usage", "running tasks", "uptime"],
            "verbs": ["monitor", "list", "check", "get"]
        },
        {
            "cmds": ["ip -c addr", "netstat -tulpn", "ss -ant", "ping -c 3 8.8.8.8"],
            "targets": ["network stats", "ip address", "connections", "port status", "connectivity"],
            "verbs": ["show", "check", "test", "display"]
        }
    ]

    augmented_data = []
    locations = ["", "locally", "recursively", "here", "in system"]

    for group in semantic_groups:
        for cmd in group["cmds"]:
            for verb, target, loc in itertools.product(group["verbs"], group["targets"], locations):
                query = f"{verb} {target} {loc}".strip()
                augmented_data.append({"nl": query, "cmd": cmd})

    final_dataset = real_data + augmented_data
    print(f"✅ Total high-fidelity dataset: {len(final_dataset)} samples.")

    # 3. Vectorization
    print("3. Initializing Transformer model...")
    model = SentenceTransformer('all-mpnet-base-v2')

    print("4. Deep Vectorization...")
    texts = [item['nl'] for item in final_dataset]
    commands = [item['cmd'] for item in final_dataset]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=256)

    # 4. FAISS Indexing
    print("5. Indexing with FAISS...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))

    # 5. Save Artifacts
    print("6. Saving Production Assets...")
    faiss.write_index(index, 'data/faiss_index.bin')
    with open('data/commands_mapping.json', 'w') as f:
        json.dump(commands, f)

    print(f"✨ Complete! Time: {round((time.time()-start_time)/60, 2)}m")

if __name__ == "__main__":
    build_pipeline()
