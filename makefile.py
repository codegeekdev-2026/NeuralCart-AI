"""
Makefile-like commands for development and deployment
Run with: python makefile.py [command]
"""

import subprocess
import sys
import os
from pathlib import Path


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(msg):
    print(f"{Colors.HEADER}{Colors.BOLD}{msg}{Colors.ENDC}")


def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")


def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")


def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")


def run_command(cmd, description=None):
    """Run a shell command"""
    if description:
        print_info(description)
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {cmd}")
        return False


def setup():
    """Setup development environment"""
    print_header("Setting up development environment...")
    
    # Create virtual environment
    run_command("python3 -m venv venv", "Creating virtual environment")
    
    # Install dependencies
    run_command("pip install -r requirements.txt", "Installing dependencies")
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    
    # Create .env if not exists
    if not Path(".env").exists():
        run_command("cp .env.example .env", "Creating .env")
        print_warning(".env created - please edit with your credentials")
    
    print_success("Setup complete!")


def lint():
    """Run code linting"""
    print_header("Running linters...")
    
    commands = [
        ("flake8 app tests", "Flake8"),
        ("black --check app tests", "Black formatter"),
        ("isort --check-only app tests", "Import sorting"),
    ]
    
    for cmd, name in commands:
        if not run_command(cmd, f"Running {name}"):
            print_warning(f"{name} check failed")


def format_code():
    """Format code"""
    print_header("Formatting code...")
    
    run_command("black app tests", "Formatting with black")
    run_command("isort app tests", "Sorting imports")
    
    print_success("Code formatted!")


def test():
    """Run tests"""
    print_header("Running tests...")
    run_command("pytest tests/ -v --cov=app --cov-report=html", "Running pytest")


def test_unit():
    """Run unit tests only"""
    print_header("Running unit tests...")
    run_command("pytest tests/ -v -m unit", "Running unit tests")


def test_integration():
    """Run integration tests"""
    print_header("Running integration tests...")
    run_command("pytest tests/ -v -m integration", "Running integration tests")


def run_server():
    """Run development server"""
    print_header("Starting development server...")
    run_command("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


def docker_build():
    """Build Docker image"""
    print_header("Building Docker image...")
    run_command("docker build -t ecommerce-api:latest .", "Building image")
    print_success("Docker image built!")


def docker_run():
    """Run Docker Compose"""
    print_header("Starting Docker Compose...")
    run_command("docker-compose up -d", "Starting services")
    print_success("Services started!")


def docker_stop():
    """Stop Docker Compose"""
    print_header("Stopping Docker Compose...")
    run_command("docker-compose down", "Stopping services")
    print_success("Services stopped!")


def docker_logs():
    """Show Docker logs"""
    run_command("docker-compose logs -f api", "Showing logs")


def clean():
    """Clean build artifacts"""
    print_header("Cleaning up...")
    
    commands = [
        ("find . -type d -name __pycache__ -exec rm -r {} +", "Removing __pycache__"),
        ("find . -type d -name .pytest_cache -exec rm -r {} +", "Removing pytest cache"),
        ("find . -type d -name .mypy_cache -exec rm -r {} +", "Removing mypy cache"),
        ("rm -rf build dist *.egg-info", "Removing build artifacts"),
        ("rm -rf htmlcov .coverage", "Removing coverage data"),
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc)
    
    print_success("Cleanup complete!")


def requirements():
    """Generate requirements.txt"""
    print_header("Generating requirements.txt...")
    run_command("pip freeze > requirements.txt", "Generating requirements")
    print_success("Requirements generated!")


def help_cmd():
    """Show help"""
    print_header("Available Commands:")
    commands = {
        "setup": "Setup development environment",
        "lint": "Run code linters",
        "format": "Format code",
        "test": "Run all tests",
        "test-unit": "Run unit tests",
        "test-integration": "Run integration tests",
        "server": "Run development server",
        "docker-build": "Build Docker image",
        "docker-run": "Start Docker Compose",
        "docker-stop": "Stop Docker Compose",
        "docker-logs": "Show Docker logs",
        "clean": "Clean build artifacts",
        "help": "Show this help message"
    }
    
    for cmd, desc in commands.items():
        print(f"  {Colors.OKBLUE}{cmd:<20}{Colors.ENDC} {desc}")


def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")


if __name__ == "__main__":
    commands = {
        "setup": setup,
        "lint": lint,
        "format": format_code,
        "test": test,
        "test-unit": test_unit,
        "test-integration": test_integration,
        "server": run_server,
        "docker-build": docker_build,
        "docker-run": docker_run,
        "docker-stop": docker_stop,
        "docker-logs": docker_logs,
        "clean": clean,
        "requirements": requirements,
        "help": help_cmd,
    }
    
    if len(sys.argv) < 2:
        help_cmd()
    else:
        cmd = sys.argv[1]
        if cmd in commands:
            commands[cmd]()
        else:
            print_error(f"Unknown command: {cmd}")
            help_cmd()
