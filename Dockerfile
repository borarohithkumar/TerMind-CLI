# 1. Start with a lightweight Python Linux environment
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies required by FAISS
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file and install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the pre-downloader and bake the AI models into the image
COPY server/predownload.py .
RUN python predownload.py

# 6. Copy the rest of your project (API script and the FAISS data folder)
COPY server/api.py .
COPY data/ ./data/

# 7. Open port 8000 for the API
EXPOSE 8000

# 8. The command to start the server when the container boots
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
