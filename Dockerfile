FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    poppler-utils \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
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
    requests \
    PyPDF2>=3.0.0

# Clone and install PDFMathTranslate
RUN git clone https://github.com/Byaidu/PDFMathTranslate.git /tmp/pdfmathtranslate \
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