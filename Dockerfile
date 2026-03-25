FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Install Python requirements
COPY ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN python -m spacy download en_core_web_sm

# Copy application files
COPY . .

# Start the continuous background worker loop
CMD ["python", "ingestion/worker.py"]
