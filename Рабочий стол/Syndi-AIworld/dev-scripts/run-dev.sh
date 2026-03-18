#!/bin/bash

# Syndi-AI Development Runner
# Usage: ./run-dev.sh [api|bot|both|test]

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Function to check virtual environment
check_venv() {
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}! Virtual environment not found${NC}"
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements_bot.txt
        echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"
    fi
}

# Function to check .env
check_env() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${YELLOW}! .env file created from template${NC}"
            echo -e "${YELLOW}! Please edit .env and add your API keys${NC}"
        fi
    fi
}

# Function to run API
run_api() {
    echo -e "${BLUE}► Starting API server...${NC}"
    check_venv
    check_env
    
    echo -e "${GREEN}✓ API starting on http://localhost:8000${NC}"
    echo -e "${GREEN}✓ Docs available at http://localhost:8000/docs${NC}"
    echo ""
    
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to run Bot
run_bot() {
    echo -e "${BLUE}► Starting Telegram Bot...${NC}"
    check_venv
    check_env
    
    echo -e "${GREEN}✓ Bot starting...${NC}"
    echo ""
    
    python -m bot.main
}

# Function to run both (background API, foreground Bot)
run_both() {
    echo -e "${BLUE}► Starting both API and Bot...${NC}"
    check_venv
    check_env
    
    # Start API in background
    echo -e "${GREEN}✓ Starting API in background...${NC}"
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
    API_PID=$!
    
    # Wait for API to start
    sleep 3
    
    echo -e "${GREEN}✓ API running on http://localhost:8000${NC}"
    echo -e "${GREEN}✓ Starting Bot...${NC}"
    echo ""
    
    # Run Bot in foreground
    python -m bot.main
    
    # Kill API when Bot stops
    kill $API_PID 2>/dev/null || true
}

# Function to run tests
run_tests() {
    echo -e "${BLUE}► Running tests...${NC}"
    check_venv
    
    pytest tests/ -v --tb=short
}

# Function to run linter
run_lint() {
    echo -e "${BLUE}► Running linters...${NC}"
    check_venv
    
    echo -e "${YELLOW}Running flake8...${NC}"
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
    
    echo -e "${YELLOW}Running black check...${NC}"
    black --check . || true
}

# Function to format code
run_format() {
    echo -e "${BLUE}► Formatting code...${NC}"
    check_venv
    
    echo -e "${YELLOW}Running black...${NC}"
    black .
    
    echo -e "${YELLOW}Running isort...${NC}"
    isort .
    
    echo -e "${GREEN}✓ Code formatted${NC}"
}

# Main menu
show_menu() {
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              Syndi-AI Development Runner                   ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Usage: ./run-dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  api      - Start API server only"
    echo "  bot      - Start Telegram Bot only"
    echo "  both     - Start both API and Bot"
    echo "  test     - Run tests"
    echo "  lint     - Run linters"
    echo "  format   - Format code with black and isort"
    echo "  setup    - Setup development environment"
    echo "  menu     - Show this menu"
    echo ""
}

# Setup function
run_setup() {
    echo -e "${BLUE}► Setting up development environment...${NC}"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    fi
    
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    pip install -r requirements_bot.txt
    
    # Install dev dependencies
    pip install pytest pytest-asyncio flake8 black isort
    
    # Create .env if not exists
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}! .env file created. Please edit it with your API keys.${NC}"
    fi
    
    # Create directories
    mkdir -p data logs
    
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Run: ./run-dev.sh api"
}

# Parse command
case "${1:-menu}" in
    api)
        run_api
        ;;
    bot)
        run_bot
        ;;
    both)
        run_both
        ;;
    test|tests)
        run_tests
        ;;
    lint)
        run_lint
        ;;
    format)
        run_format
        ;;
    setup)
        run_setup
        ;;
    menu|help|-h|--help)
        show_menu
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_menu
        exit 1
        ;;
esac
