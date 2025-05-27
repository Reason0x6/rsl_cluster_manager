# Use a base image (e.g., Python if your app is Python-based)
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on (adjust as needed)
EXPOSE 8000

# Define the command to run your app
CMD ["python", "app.py"]