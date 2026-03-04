"""
Project initialization and verification script
Helps with getting started and verifying the setup
"""

import os
from pathlib import Path


class ProjectValidator:
    """Validates project structure and setup"""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root)
        self.required_files = [
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            ".env.example",
            "README.md",
            "pytest.ini",
        ]
        
        self.required_dirs = [
            "app",
            "app/api",
            "app/agents",
            "app/services",
            "app/models",
            "app/utils",
            "app/integrations",
            "app/config",
            "tests",
            "aws",
            ".github/workflows"
        ]
    
    def check_structure(self) -> bool:
        """Check if project structure is complete"""
        print("Checking project structure...")
        
        all_good = True
        
        # Check files
        for file in self.required_files:
            path = self.root / file
            if path.exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} - MISSING")
                all_good = False
        
        # Check directories
        for dir_name in self.required_dirs:
            path = self.root / dir_name
            if path.exists():
                print(f"  ✅ {dir_name}/")
            else:
                print(f"  ❌ {dir_name}/ - MISSING")
                all_good = False
        
        return all_good
    
    def count_files(self) -> dict:
        """Count files in project"""
        counts = {
            "python": 0,
            "yaml": 0,
            "markdown": 0,
            "shell": 0,
            "json": 0,
            "dockerfile": 0,
            "total": 0
        }
        
        for root, dirs, files in os.walk(self.root):
            # Skip virtual env and git
            if any(skip in root for skip in ['venv', '.git', '__pycache__', '.pytest']):
                continue
            
            for file in files:
                counts["total"] += 1
                
                if file.endswith(".py"):
                    counts["python"] += 1
                elif file.endswith((".yml", ".yaml")):
                    counts["yaml"] += 1
                elif file.endswith(".md"):
                    counts["markdown"] += 1
                elif file.endswith(".sh"):
                    counts["shell"] += 1
                elif file.endswith(".json"):
                    counts["json"] += 1
                elif file == "Dockerfile":
                    counts["dockerfile"] += 1
        
        return counts
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions"""
        return """
╔════════════════════════════════════════════════════════════════╗
║  E-commerce Personalization Platform - Setup Instructions      ║
╚════════════════════════════════════════════════════════════════╝

1. ENVIRONMENT SETUP
   cp .env.example .env
   # Edit .env with your API keys:
   #   - OPENAI_API_KEY
   #   - STRIPE_API_KEY
   #   - AWS credentials (optional)

2. PYTHON ENVIRONMENT
   python -m venv venv
   source venv/bin/activate          # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt

3. DOCKER STARTUP
   docker-compose up -d
   # Services: API, PostgreSQL, Redis, ElasticSearch

4. START API (Choose one)
   
   Option A - Command line:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   Option B - Python module:
   python -m app.main
   
   Option C - With helpers:
   python makefile.py server

5. ACCESS API
   API:  http://localhost:8000
   Docs: http://localhost:8000/docs
   ReDoc: http://localhost:8000/redoc

6. TEST THE API
   # Run tests
   pytest tests/ -v
   
   # Or run examples
   python examples.py
   
   # Or use makefile
   python makefile.py test

7. COMMON COMMANDS
   # Run linting
   python makefile.py lint
   
   # Format code
   python makefile.py format
   
   # Clean build artifacts
   python makefile.py clean
   
   # View all commands
   python makefile.py help

8. DOCUMENTATION
   - API Reference: See API_REFERENCE.md
   - Architecture: See AGENT_ARCHITECTURE.md
   - Deployment: See DEPLOYMENT.md
   - Roadmap: See ROADMAP.md

9. DEBUGGING
   # Check health
   curl http://localhost:8000/health
   
   # Check readiness
   curl http://localhost:8000/ready
   
   # View configuration
   curl http://localhost:8000/config

10. NEXT STEPS
    - Configure your API keys in .env
    - Review API documentation
    - Test recommendation endpoints
    - Explore agent reasoning
    - Plan deployment strategy

Questions? Check README.md for more details.
"""
    
    def run_verification(self):
        """Run full verification"""
        print("\n" + "="*60)
        print("Project Structure Validation")
        print("="*60 + "\n")
        
        # Check structure
        if self.check_structure():
            print("\n✅ Project structure is complete!\n")
        else:
            print("\n❌ Some files/folders are missing!\n")
            return False
        
        # Count files
        counts = self.count_files()
        print("\nProject Statistics:")
        print(f"  Python files:      {counts['python']}")
        print(f"  YAML files:        {counts['yaml']}")
        print(f"  Markdown files:    {counts['markdown']}")
        print(f"  Shell scripts:     {counts['shell']}")
        print(f"  Total files:       {counts['total']}")
        
        # Print setup instructions
        print(self.get_setup_instructions())
        
        return True


if __name__ == "__main__":
    validator = ProjectValidator()
    validator.run_verification()
