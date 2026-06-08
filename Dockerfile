FROM python:3.12-slim

# Install system dependencies required for video/image processing and browser automation
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick security policy for MoviePy
# By default, ImageMagick disables reading/writing of some formats for security on web servers.
RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<!-- <policy domain="path" rights="none" pattern="@\*"\/> -->/g' /etc/ImageMagick-6/policy.xml || true

# Set working directory
WORKDIR /app

# Copy project configuration
COPY pyproject.toml .

# Install dependencies (ignoring missing code for now to just get the deps installed)
RUN pip install --no-cache-dir -e .

# Install Playwright browsers (required by composio / script generators)
RUN playwright install --with-deps chromium

# Copy application source code
COPY . .

# Environment configuration
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Command to run the scheduler
CMD ["python", "scheduler.py"]
