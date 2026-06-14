#!/bin/bash

# SPECTER Quick Start Script
# This script helps you get SPECTER up and running quickly

set -e

echo "=================================="
echo "SPECTER Quick Start"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    echo -e "${RED}Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

# Check pip
echo "Checking pip installation..."
if command_exists pip3; then
    echo -e "${GREEN}✓ pip3 installed${NC}"
else
    echo -e "${RED}✗ pip3 not found. Please install pip.${NC}"
    exit 1
fi

# Check Node.js
echo "Checking Node.js installation..."
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Node.js not found. Required for frontend.${NC}"
    echo "Install from: https://nodejs.org/"
fi

# Check npm
echo "Checking npm installation..."
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ npm $NPM_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ npm not found. Required for frontend.${NC}"
fi

echo ""
echo "=================================="
echo "Installing Backend Dependencies"
echo "=================================="
echo ""

cd backend

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -r requirements.txt

echo ""
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Check for Tesseract (OCR)
echo ""
echo "Checking OCR dependencies..."
if command_exists tesseract; then
    echo -e "${GREEN}✓ Tesseract OCR installed${NC}"
else
    echo -e "${YELLOW}⚠ Tesseract OCR not found${NC}"
    if [[ "$OS" == "macOS" ]]; then
        echo "Install with: brew install tesseract"
    else
        echo "Install with: sudo apt-get install tesseract-ocr"
    fi
fi

# Check for Poppler (PDF processing)
if [[ "$OS" == "macOS" ]]; then
    if command_exists pdfinfo; then
        echo -e "${GREEN}✓ Poppler installed${NC}"
    else
        echo -e "${YELLOW}⚠ Poppler not found${NC}"
        echo "Install with: brew install poppler"
    fi
fi

# Check for MongoDB
echo ""
echo "Checking MongoDB..."
if command_exists mongod; then
    echo -e "${GREEN}✓ MongoDB installed${NC}"
else
    echo -e "${YELLOW}⚠ MongoDB not found${NC}"
    echo "You can use MongoDB Atlas (cloud) or install locally"
    echo "MongoDB Atlas: https://www.mongodb.com/cloud/atlas"
fi

# Check for Ollama
echo ""
echo "Checking Ollama (LLM)..."
if command_exists ollama; then
    echo -e "${GREEN}✓ Ollama installed${NC}"
    
    # Check if llama2 model is available
    if ollama list | grep -q "llama2"; then
        echo -e "${GREEN}✓ llama2 model available${NC}"
    else
        echo -e "${YELLOW}⚠ llama2 model not found${NC}"
        echo "Pull with: ollama pull llama2"
    fi
else
    echo -e "${YELLOW}⚠ Ollama not found${NC}"
    echo "Install from: https://ollama.com/"
    echo "After installation, run: ollama pull llama2"
fi

# Check for .env file
echo ""
echo "Checking configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
else
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your configuration${NC}"
fi

cd ..

# Frontend setup
echo ""
echo "=================================="
echo "Installing Frontend Dependencies"
echo "=================================="
echo ""

if command_exists npm; then
    cd frontend/react_app
    
    echo "Installing npm packages..."
    npm install
    
    echo ""
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    
    cd ../..
else
    echo -e "${YELLOW}⚠ Skipping frontend setup (npm not found)${NC}"
fi

# Run tests
echo ""
echo "=================================="
echo "Running System Tests"
echo "=================================="
echo ""

cd backend
python3 test_system.py
cd ..

# Summary
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure .env file:"
echo "   cd backend"
echo "   nano .env"
echo ""
echo "2. Start MongoDB (if using local):"
echo "   mongod"
echo ""
echo "3. Start Ollama (for LLM features):"
echo "   ollama serve"
echo ""
echo "4. Start Backend:"
echo "   cd backend"
echo "   uvicorn main:app --reload --port 8002"
echo ""
echo "5. Start Frontend (in new terminal):"
echo "   cd frontend/react_app"
echo "   npm run dev"
echo ""
echo "6. Open browser:"
echo "   http://localhost:5173"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
