#!/bin/bash

# Syndi-AI Setup Script
# Usage: ./setup.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Syndi-AI Setup                          ║"
echo "║         AI-Powered Professional Collaboration              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${GREEN}✓ Python version is compatible${NC}"
else
    echo -e "${RED}✗ Python 3.10+ is required${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}! Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo ""
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
pip install -r requirements_bot.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file
echo ""
echo -e "${YELLOW}Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created from template${NC}"
    echo -e "${YELLOW}! Please edit .env and add your API keys${NC}"
else
    echo -e "${YELLOW}! .env file already exists${NC}"
fi

# Create directories
echo ""
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data logs static
echo -e "${GREEN}✓ Directories created${NC}"

# Run tests
echo ""
echo -e "${YELLOW}Running tests...${NC}"
if pytest tests/ -v --tb=short 2>/dev/null; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}! Some tests failed (this is OK if you haven't configured API keys)${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "  1. Edit .env file and add your API keys:"
echo "     - TELEGRAM_TOKEN (from @BotFather)"
echo "     - DEEPSEEK_API_KEY (from DeepSeek)"
echo "     - IONQ_API_KEY (optional, for quantum computing)"
echo ""
echo "  2. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  3. Start the API server:"
echo "     make run-api"
echo ""
echo "  4. Start the Telegram bot (in another terminal):"
echo "     make run-bot"
echo ""
echo "  Or use Docker:"
echo "     docker-compose up -d"
echo ""
echo "  API Documentation: http://localhost:8000/docs"
echo ""
