FROM python:3.11-slim

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Mark GitHub workspace as safe
RUN git config --global --add safe.directory /github/workspace

WORKDIR /action

COPY . /action

RUN pip install --upgrade pip
RUN pip install -r /action/src/llm/requirements.txt

ENTRYPOINT ["python", "/action/scripts/run_action.py"]
