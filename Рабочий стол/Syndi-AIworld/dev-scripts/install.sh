#!/bin/bash

# Syndi-AI Development Environment Installer
# Usage: ./install.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Syndi-AI Development Environment Setup                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Python version
echo -e "${BLUE}► Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${GREEN}✓ Python version is compatible (3.10+)${NC}"
else
    echo -e "${RED}✗ Python 3.10+ is required${NC}"
    exit 1
fi
echo ""

# Create virtual environment
echo -e "${BLUE}► Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}! Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${BLUE}► Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${BLUE}► Upgrading pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}► Installing dependencies...${NC}"
pip install -r requirements.txt
pip install -r requirements_bot.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Install development dependencies
echo -e "${BLUE}► Installing development tools...${NC}"
pip install pytest pytest-asyncio flake8 black isort mypy
echo -e "${GREEN}✓ Development tools installed${NC}"
echo ""

# Create .env file
echo -e "${BLUE}► Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created from template${NC}"
        echo -e "${YELLOW}! Please edit .env and add your API keys${NC}"
    else
        echo -e "${YELLOW}! .env.example not found, skipping${NC}"
    fi
else
    echo -e "${YELLOW}! .env file already exists${NC}"
fi
echo ""

# Create directories
echo -e "${BLUE}► Creating directories...${NC}"
mkdir -p data logs static
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Run tests
echo -e "${BLUE}► Running tests...${NC}"
if pytest tests/ -v --tb=short 2>/dev/null; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}! Some tests failed (this is OK if you haven't configured API keys)${NC}"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Setup Complete!                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Development environment is ready!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Edit .env file and add your API keys:"
echo "     - TELEGRAM_TOKEN (from @BotFather)"
echo "     - DEEPSEEK_API_KEY (from platform.deepseek.com)"
echo ""
echo "  2. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  3. Start the API server:"
echo "     ./run-dev.sh api"
echo ""
echo "  4. Start the Telegram bot (in another terminal):"
echo "     ./run-dev.sh bot"
echo ""
echo "  Or start both:"
echo "     ./run-dev.sh both"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
