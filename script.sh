#!/usr/bin/env bash
# scripts/dev - Development helper scripts for PrompTrek

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

cd "$PROJECT_ROOT"

case "${1:-help}" in
    help)
        echo -e "${BLUE}PrompTrek Development Helper${NC}"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo -e "  ${GREEN}setup${NC}      - Initial project setup with uv"
        echo -e "  ${GREEN}install${NC}    - Install dependencies with uv"  
        echo -e "  ${GREEN}test${NC}       - Run tests"
        echo -e "  ${GREEN}lint${NC}       - Run linters"
        echo -e "  ${GREEN}format${NC}     - Format code"
        echo -e "  ${GREEN}build${NC}      - Build package"
        echo -e "  ${GREEN}clean${NC}      - Clean artifacts"
        echo -e "  ${GREEN}run${NC}        - Run promptrek CLI"
        echo ""
        echo -e "For more options, use: ${YELLOW}make help${NC}"
        ;;
    setup)
        echo -e "${BLUE}Setting up PrompTrek development environment...${NC}"
        if ! command -v uv &> /dev/null; then
            echo -e "${RED}Error: uv is not installed. Please install uv first:${NC}"
            echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
            exit 1
        fi
        echo -e "${YELLOW}Installing dependencies...${NC}"
        uv sync --group dev
        echo -e "${GREEN}Setup complete! You can now run tests with: $0 test${NC}"
        ;;
    install)
        echo -e "${BLUE}Installing dependencies...${NC}"
        uv sync --group dev
        ;;
    test)
        echo -e "${BLUE}Running tests...${NC}"
        uv run python -m pytest "${@:2}"
        ;;
    lint)
        echo -e "${BLUE}Running linters...${NC}"
        uv run black --check src/ tests/
        uv run isort --check-only src/ tests/
        uv run flake8 src/ tests/
        ;;
    format)
        echo -e "${BLUE}Formatting code...${NC}"
        uv run black src/ tests/
        uv run isort src/ tests/
        ;;
    build)
        echo -e "${BLUE}Building package...${NC}"
        uv build
        ;;
    clean)
        echo -e "${BLUE}Cleaning artifacts...${NC}"
        rm -rf dist/ build/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete
        ;;
    run)
        echo -e "${BLUE}Running promptrek...${NC}"
        uv run promptrek "${@:2}"
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Run '$0 help' for available commands"
        exit 1
        ;;
esac