# ☁️ TerMind (Terminal + Mind)

An Enterprise-Grade, ML-Powered Hybrid NLP-to-Bash DevOps CLI.

TerMind is a modern, distributed microservice that allows developers and system administrators to control their Linux and Docker environments using natural language. It translates human intent into accurate, executable Bash commands in milliseconds.

## The Hybrid Architecture

TerMind solves the latency and hallucination problems of standard LLMs by using a Hybrid Routing Engine (inspired by research in Natural Language Translation for OS commands):

- **Path A (The High-Speed Brain)**: A pre-compiled FAISS vector index holding 42,000+ verified DevOps commands. Powered by all-mpnet-base-v2, it performs semantic mathematical matching in milliseconds.
- **Path B (The Generative Fallback)**: If a query is entirely novel (low confidence score), the system dynamically falls back to a locally hosted T5-Base generative neural network to synthesize a brand new command.

## Tech Stack

- **Cloud Backend**: FastAPI, Uvicorn, AWS EC2, Docker
- **Machine Learning**: PyTorch, HuggingFace Transformers, FAISS (Facebook AI Similarity Search)
- **Client / CLI**: Python, Bash, Termux Android Support

## Installation (Linux & Termux)

The client is a zero-dependency Python wrapper. The installation script automatically builds an isolated, protected virtual environment and maps the executable to your system's PATH.

```bash
git clone https://github.com/borarohithkumar/TerMind-CLI.git
cd TerMind-CLI
chmod +x install.sh
./install.sh
```

> After installing, remember to `source ~/.zshrc` or `source ~/.bashrc` if prompted!

## Usage

Once installed, summon the AI from anywhere in your system:

```bash
termind
```

### Example Interaction:

```
TerMind> find all files modified in the last 7 days
--------------------------------------------------
⚙️ System   : find -daystart -mtime -7
🧠 Engine   : FAISS Semantic Match (High Confidence)
--------------------------------------------------
Execute this command locally? [y/N]: y
```

## Repository Structure

- `/server`: The FastAPI Python backend and Docker build scripts.
- `/client`: The lightweight network CLI tool.
- `/data`: Holds the 125MB FAISS binary index and command mappings.
- `/scripts`: The Data Engineering pipeline. Contains the algorithms used to mathematically augment HuggingFace datasets (westenfelder/NL2SH-ALFA) into a 42,000+ parameter vector index.

## 🐳 Cloud Deployment

The backend is containerized for zero-downtime deployment. The HuggingFace ML models are pre-baked into the Docker image layer to ensure rapid boot times without downloading gigabytes of weights on restart.

[![Docker Image Version](https://img.shields.io/docker/v/borarohithkumar/termind-api?sort=semver&label=Docker%20Hub)](https://hub.docker.com/r/borarohithkumar/termind-api)

You can pull the official pre-compiled Machine Learning backend directly from Docker Hub:

```bash
docker pull borarohithkumar/termind-api:v2.0
docker run -d -p 8000:8000 borarohithkumar/termind-api:v2.0
```

_For more details, see the [official container documentation](https://hub.docker.com/r/borarohithkumar/termind-api) on Docker Hub._
