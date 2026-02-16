FROM python:3.11-slim

# Put action code somewhere safe
WORKDIR /action

# Copy action files into image
COPY . /action

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /action/src/llm/requirements.txt

# Run using absolute path
ENTRYPOINT ["python", "/action/scripts/run_action.py"]
