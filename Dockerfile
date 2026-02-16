FROM python:3.11-slim

WORKDIR /action

# Copy entire action repository into container
COPY . /action

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r src/llm/requirements.txt

# Default entrypoint
ENTRYPOINT ["python", "scripts/run_action.py"]
