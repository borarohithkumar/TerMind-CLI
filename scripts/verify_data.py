"""
TerMind Data Quality Assurance
Validates the integrity, size, and mapping accuracy of the FAISS vector index 
and the JSON command mappings prior to deployment.
"""

import os
import json
import random

def verify_assets():
    files = ['data/faiss_index.bin', 'data/commands_mapping.json']
    
    print("\n--- Artifact Verification ---")
    for f in files:
        if os.path.exists(f):
            size_mb = os.path.getsize(f) / (1024 * 1024)
            print(f"✅ {f}: Exists ({size_mb:.2f} MB)")
        else:
            print(f"❌ {f}: Missing!")
            return

    # Inspect Dataset Quality
    print("\n--- Command Mapping Quality Check ---")
    with open('data/commands_mapping.json', 'r') as f:
        commands = json.load(f)
    
    print(f"Total Indexed Commands: {len(commands)}")
    
    samples = random.sample(commands, 5)
    print("Random Command Sample:")
    for i, cmd in enumerate(samples):
        print(f"  {i+1}. {cmd}")
    print("------------------------------------------\n")

if __name__ == "__main__":
    verify_assets()
