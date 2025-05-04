#!/bin/bash
# run.sh - Helper script for building and running the PDF translator

# Stop on errors
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default values
IMAGE_NAME="pdf-translator"
CONTAINER_NAME="pdf-translator-container"
INPUT_DIR="$SCRIPT_DIR/data"
OUTPUT_DIR="$SCRIPT_DIR/data"

# Help message
show_help() {
    echo "Usage: $0 [options] [-- command args...]"
    echo ""
    echo "Options:"
    echo "  -h, --help             Show this help message"
    echo "  -b, --build            Build/rebuild the Docker image"
    echo "  -i, --input DIR        Set input directory (default: ./data)"
    echo "  -o, --output DIR       Set output directory (default: ./data)"
    echo ""
    echo "Examples:"
    echo "  $0 --build                         # Build the Docker image"
    echo "  $0 data/input.pdf                  # Translate input.pdf with default settings"
    echo "  $0 data/input.pdf -s english -t japanese -e openai  # Translate with OpenAI"
    echo ""
    exit 0
}

# Parse options
BUILD=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            ;;
        -b|--build)
            BUILD=1
            shift
            ;;
        -i|--input)
            INPUT_DIR="$(cd "$2" && pwd)"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$(cd "$2" && pwd)"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            break
            ;;
    esac
done

# Create data directory if it doesn't exist
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

# Build the image if requested
if [ $BUILD -eq 1 ]; then
    echo "Building Docker image: $IMAGE_NAME"
    docker build -t "$IMAGE_NAME" .
fi

# Check if image exists, build if not
if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo "Image doesn't exist, building..."
    docker build -t "$IMAGE_NAME" .
fi

# Prepare the container run command
CMD="docker run --rm -it"
CMD="$CMD --name $CONTAINER_NAME"
CMD="$CMD -v $INPUT_DIR:/app/data/input"
CMD="$CMD -v $OUTPUT_DIR:/app/data/output"
CMD="$CMD -v $SCRIPT_DIR/.env:/app/.env"
CMD="$CMD $IMAGE_NAME"

# If arguments were provided, add them
if [ $# -gt 0 ]; then
    # Map the first argument (input file) to the container's path if it's in the current directory
    if [[ -f "$1" && "$1" == */* ]]; then
        # Get the filename without path
        FILE_NAME=$(basename "$1")
        
        # Check if the file is in the data directory
        if [[ "$1" == *"data/"* ]]; then
            # File is in the data directory, use the proper container path
            ARGS="/app/data/input/$FILE_NAME"
            shift
            CMD="$CMD python translate.py $ARGS $@"
        else
            # Just pass all arguments as-is
            CMD="$CMD python translate.py $@"
        fi
    else
        # Just pass all arguments as-is
        CMD="$CMD python translate.py $@"
    fi
else
    # No arguments, show help
    CMD="$CMD python translate.py --help"
fi

# Execute the command
echo "Running: $CMD"
eval "$CMD"