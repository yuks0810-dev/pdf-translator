FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install PDFMathTranslate from the original repository
RUN pip install --no-cache-dir \
    pdfminer.six \
    pymupdf \
    openai \
    google-generativeai \
    anthropic \
    python-dotenv \
    reportlab \
    requests

# Clone and install PDFMathTranslate
RUN git clone https://github.com/ptyin/PDFMathTranslate.git /tmp/pdfmathtranslate \
    && cd /tmp/pdfmathtranslate \
    && pip install -e . \
    && cd / \
    && rm -rf /tmp/pdfmathtranslate/.git

# Create directories for input/output
RUN mkdir -p /app/data/input /app/data/output

# Copy our application files
COPY requirements.txt .
COPY *.py .
COPY .env .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command
CMD ["python", "translate.py", "--help"]