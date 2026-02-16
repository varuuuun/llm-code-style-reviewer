FROM python:3.11-slim

# Install git (required for detecting changed files)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /action

COPY . /action

RUN pip install --upgrade pip
RUN pip install -r /action/src/llm/requirements.txt

ENTRYPOINT ["python", "/action/scripts/run_action.py"]
