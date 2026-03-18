#!/bin/bash
# Syndi-AI Repository Reorganization Script
# Usage: ./reorganize_repo.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Syndi-AI: Наведение порядка в репозитории              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if we're in git repo
if [ ! -d ".git" ]; then
    echo -e "${RED}✗ Это не Git репозиторий!${NC}"
    exit 1
fi

echo -e "${BLUE}► Текущая директория: $(pwd)${NC}"
echo ""

# Step 1: Create directory structure
echo -e "${YELLOW}Шаг 1: Создание структуры директорий...${NC}"
mkdir -p api bot core/{agents,ai,matching,mystic,quantum} models services tests docs
echo -e "${GREEN}✓ Директории созданы${NC}"
echo ""

# Step 2: Move files to correct locations
echo -e "${YELLOW}Шаг 2: Перемещение файлов...${NC}"

# API files
[ -f "main.py" ] && mv main.py api/ 2>/dev/null || true
echo -e "${GREEN}  ✓ api/main.py${NC}"

# Bot files
[ -f "bot_main.py" ] && mv bot_main.py bot/main.py 2>/dev/null || true
echo -e "${GREEN}  ✓ bot/main.py${NC}"

# Core - Agents
[ -f "kristina.py" ] && mv kristina.py core/agents/ 2>/dev/null || true
[ -f "base.py" ] && mv base.py core/agents/ 2>/dev/null || true
echo -e "${GREEN}  ✓ core/agents/${NC}"

# Core - AI
[ -f "llm.py" ] && mv llm.py core/ai/ 2>/dev/null || true
[ -f "deepseek.py" ] && mv deepseek.py core/ai/ 2>/dev/null || true
echo -e "${GREEN}  ✓ core/ai/${NC}"

# Core - Matching
[ -f "matching.py" ] && mv matching.py core/matching/ 2>/dev/null || true
echo -e "${GREEN}  ✓ core/matching/${NC}"

# Core - Mystic
[ -f "mbti.py" ] && mv mbti.py core/mystic/ 2>/dev/null || true
[ -f "enneagram.py" ] && mv enneagram.py core/mystic/ 2>/dev/null || true
[ -f "tarot.py" ] && mv tarot.py core/mystic/ 2>/dev/null || true
[ -f "psychomatrix.py" ] && mv psychomatrix.py core/mystic/ 2>/dev/null || true
[ -f "baizi.py" ] && mv baizi.py core/mystic/ 2>/dev/null || true
[ -f "biorhythm.py" ] && mv biorhythm.py core/mystic/ 2>/dev/null || true
[ -f "interpretation.py" ] && mv interpretation.py core/mystic/ 2>/dev/null || true
[ -f "advice.py" ] && mv advice.py core/mystic/ 2>/dev/null || true
[ -f "analysis.py" ] && mv analysis.py core/mystic/ 2>/dev/null || true
[ -f "visuals.py" ] && mv visuals.py core/mystic/ 2>/dev/null || true
echo -e "${GREEN}  ✓ core/mystic/${NC}"

# Core - Quantum
[ -f "ionq_integration.py" ] && mv ionq_integration.py core/quantum/ 2>/dev/null || true
[ -f "generator.py" ] && mv generator.py core/quantum/ 2>/dev/null || true
[ -f "quantum_analysis.py" ] && mv quantum_analysis.py core/quantum/ 2>/dev/null || true
echo -e "${GREEN}  ✓ core/quantum/${NC}"

# Models
[ -f "user.py" ] && mv user.py models/ 2>/dev/null || true
[ -f "big_five.py" ] && mv big_five.py models/ 2>/dev/null || true
[ -f "models_bot.py" ] && mv models_bot.py models/bot.py 2>/dev/null || true
[ -f "mystic.py" ] && mv mystic.py models/ 2>/dev/null || true
echo -e "${GREEN}  ✓ models/${NC}"

# Services
[ -f "services_llm.py" ] && mv services_llm.py services/llm.py 2>/dev/null || true
[ -f "services_matching.py" ] && mv services_matching.py services/matching.py 2>/dev/null || true
echo -e "${GREEN}  ✓ services/${NC}"

# Tests
[ -f "test_agents.py" ] && mv test_agents.py tests/ 2>/dev/null || true
[ -f "test_big_five.py" ] && mv test_big_five.py tests/ 2>/dev/null || true
[ -f "test_matching.py" ] && mv test_matching.py tests/ 2>/dev/null || true
echo -e "${GREEN}  ✓ tests/${NC}"

# Docs
[ -f "DEEPSEEK_SETUP.md" ] && mv DEEPSEEK_SETUP.md docs/ 2>/dev/null || true
[ -f "GITHUB_SETUP.md" ] && mv GITHUB_SETUP.md docs/ 2>/dev/null || true
[ -f "PROJECT_REPORT.md" ] && mv PROJECT_REPORT.md docs/ 2>/dev/null || true
echo -e "${GREEN}  ✓ docs/${NC}"

echo ""

# Step 3: Remove Git internal files
echo -e "${YELLOW}Шаг 3: Удаление Git-файлов...${NC}"
GIT_FILES=("COMMIT_EDITMSG" "HEAD" "config" "description" "index" "main")
for file in "${GIT_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo -e "${GREEN}  ✓ Удален: $file${NC}"
    fi
done
echo ""

# Step 4: Remove duplicate files
echo -e "${YELLOW}Шаг 4: Удаление дубликатов...${NC}"
DUPLICATES=("generator.py.1" "ionq_integration.py.1")
for file in "${DUPLICATES[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo -e "${GREEN}  ✓ Удален дубликат: $file${NC}"
    fi
done
echo ""

# Step 5: Remove unnecessary files
echo -e "${YELLOW}Шаг 5: Удаление ненужных файлов...${NC}"
UNNECESSARY=("GITHUB_UPLOAD.md" "SYNDI_PERSISTENT_CONTEXT.md")
for file in "${UNNECESSARY[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo -e "${GREEN}  ✓ Удален: $file${NC}"
    fi
done
echo ""

# Step 6: Create __init__.py files
echo -e "${YELLOW}Шаг 6: Создание __init__.py...${NC}"
touch api/__init__.py
for dir in api bot core core/{agents,ai,matching,mystic,quantum} models services tests; do
    if [ -d "$dir" ] && [ ! -f "$dir/__init__.py" ]; then
        touch "$dir/__init__.py"
        echo -e "${GREEN}  ✓ $dir/__init__.py${NC}"
    fi
done
echo ""

# Step 7: Update .gitignore
echo -e "${YELLOW}Шаг 7: Обновление .gitignore...${NC}"
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Data
data/*.json
!data/.gitkeep

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Git internals (should never be committed)
COMMIT_EDITMSG
HEAD
config
description
index

# Temporary files
*.tmp
*.bak
*.1
*.2
*.orig
EOF
echo -e "${GREEN}✓ .gitignore обновлен${NC}"
echo ""

# Step 8: Show final structure
echo -e "${YELLOW}Шаг 8: Итоговая структура...${NC}"
echo ""
tree -L 3 -I '__pycache__|*.pyc' . 2>/dev/null || find . -type f -not -path './.git/*' -not -name '*.pyc' | head -40
echo ""

# Step 9: Git operations
echo -e "${YELLOW}Шаг 9: Git операции...${NC}"
echo -e "${BLUE}► Добавление изменений...${NC}"
git add -A
echo -e "${GREEN}✓ Файлы добавлены${NC}"

echo ""
echo -e "${BLUE}► Создание коммита...${NC}"
git commit -m "Reorganize repository structure

- Organized files into proper directory structure
- Moved source files to api/, bot/, core/, models/, services/
- Removed Git internal files (COMMIT_EDITMSG, HEAD, config, etc.)
- Removed duplicate files (generator.py.1, ionq_integration.py.1)
- Removed unnecessary files (GITHUB_UPLOAD.md, SYNDI_PERSISTENT_CONTEXT.md)
- Added __init__.py to all Python packages
- Updated .gitignore with proper exclusions

New structure:
├── api/          # FastAPI endpoints
├── bot/          # Telegram bot
├── core/         # Core modules
│   ├── agents/   # AI agents
│   ├── ai/       # LLM integration
│   ├── matching/ # Matching algorithm
│   ├── mystic/   # MBTI, Enneagram, Tarot
│   └── quantum/  # Quantum computing
├── models/       # Pydantic models
├── services/     # Business logic
├── tests/        # Unit tests
└── docs/         # Documentation" || echo -e "${YELLOW}! Нет изменений для коммита${NC}"

echo ""
echo -e "${BLUE}► Отправка на GitHub...${NC}"
git push origin main && echo -e "${GREEN}✓ Отправлено на GitHub${NC}" || echo -e "${RED}✗ Ошибка отправки${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Реорганизация завершена!                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Репозиторий приведен в порядок${NC}"
echo ""
echo "Проверьте результат на GitHub:"
echo "  https://github.com/donjonson-hash/Syndi-AI-world"
echo ""
