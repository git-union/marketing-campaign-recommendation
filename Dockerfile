# Use an official Python runtime as a parent image.
FROM python:3.9-slim

# Set environment variables to ensure output is not buffered.
ENV PYTHONUNBUFFERED=1

# Create and change to the app directory.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose the port on which your app runs.
EXPOSE 3000

# Run the application using gunicorn.
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "server:app"]
