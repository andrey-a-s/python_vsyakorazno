FROM python:3.9-slim

# Install Python dependencies
RUN pip install --no-cache-dir pyyaml

# Add the script to the container
COPY find_in_yaml.py /usr/local/bin/find_in_yaml.py

# Set the entrypoint
ENTRYPOINT ["python", "/usr/local/bin/find_in_yaml.py"]
