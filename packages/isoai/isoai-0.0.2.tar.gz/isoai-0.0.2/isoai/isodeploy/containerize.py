"""Containerize your model for production easily."""
import os

class Containerize:
    """A class to evaluate model size and create an optimized Dockerfile for containerization.
    """

    BASE_IMAGES = {
        'small': 'python:3.9-slim',
        'medium': 'python:3.9',
        'large': 'ubuntu:20.04'
    }

    def __init__(self, model_path):
        """Initialize the Containerize class with the model path.

        Args:
            model_path (str): The file path to the model.
        """
        self.model_path = model_path
        self.model_size = self.evaluate_model_size()

    def evaluate_model_size(self):
        """Evaluate the size of the model.

        Returns:
            str: The size category of the model ('small', 'medium', 'large').
        """
        size_in_mb = os.path.getsize(self.model_path) / (1024 * 1024)
        if size_in_mb < 100:
            return 'small'
        elif size_in_mb < 500:
            return 'medium'
        else:
            return 'large'

    def select_base_image(self):
        """Select the best base image based on model size.

        Returns:
            str: The selected base image.
        """
        return self.BASE_IMAGES[self.model_size]

    def create_dockerfile(self, output_path):
        """Create a Dockerfile using a multi-stage build and optimize for production.

        Args:
            output_path (str): The file path to save the Dockerfile.
        """
        base_image = self.select_base_image()
        
        dockerfile_content = f"""
        # Stage 1: Build Stage
        FROM {base_image} AS builder

        # Install dependencies
        RUN apt-get update && apt-get install -y --no-install-recommends \\
            build-essential \\
            && rm -rf /var/lib/apt/lists/*

        # Set working directory
        WORKDIR /app

        # Copy model files
        COPY . .

        # Stage 2: Production Stage
        FROM {base_image}

        # Install necessary packages
        RUN apt-get update && apt-get install -y --no-install-recommends \\
            ca-certificates \\
            && rm -rf /var/lib/apt/lists/*

        # Set working directory
        WORKDIR /app

        # Copy from the build stage
        COPY --from=builder /app /app

        # Install Python packages
        RUN pip install --no-cache-dir -r requirements.txt

        # Set environment variables for production
        ENV PYTHONUNBUFFERED=1

        # Run the application
        CMD ["python", "your_model_script.py"]
        """
        
        with open(output_path, 'w') as file:
            file.write(dockerfile_content.strip())

    def run(self, output_path):
        """Execute the process to create an optimized Dockerfile.

        Args:
            output_path (str): The file path to save the Dockerfile.
        """
        self.create_dockerfile(output_path)

