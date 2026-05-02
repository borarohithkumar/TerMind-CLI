"""
TerMind Cloud CLI
A lightweight, zero-dependency Python client that routes natural language
prompts to the TerMind AWS Microservice and safely executes the returned Bash commands.
"""

import requests
import subprocess
import sys

# Production Server Endpoint (AWS Microservice) or 127.0.0.1 for local testing
API_URL = "http://18.60.42.147:8000/translate"

def print_banner():
    """Renders the CLI UI banner."""
    print("\n" + "="*55)
    print(" ☁️   TerMind CLOUD CLI v2.0. Type 'exit' to quit.")
    print("="*55 + "\n")

def main():
    print_banner()

    while True:
        try:
            # Capture user intent
            user_input = input("\nTerMind> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input.strip():
                continue

            # 1. Network Request Layer
            try:
                response = requests.post(API_URL, json={"query": user_input})
                response.raise_for_status() 
                data = response.json()
            except requests.exceptions.ConnectionError:
                print("❌ Network Error: Could not connect to the TerMind backend.")
                continue
            
            final_cmd = data["final_command"]
            logic = data["logic_used"]

            # Display AI suggestion
            print("\n" + "-"*50)
            print("\n" + "-"*50)
            print(f"⚙️  System   : {final_cmd}")
            print(f"🧠 Engine   : {logic}")
            print("-" * 50)

            # 2. Safety & Execution Layer
            confirm = input("\nExecute this command locally? [y/N]: ")
            if confirm.lower() == 'y':
                print("\nExecuting...\n")
                subprocess.run(final_cmd, shell=True, text=True)
            else:
                print("Execution cancelled.")

        except KeyboardInterrupt:
            # Graceful exit on Ctrl+C
            print("\nExiting TerMind...")
            sys.exit(0)

if __name__ == "__main__":
    main()
