# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with Python projects.

## Basic Project Structure & Commands

### Environment Setup
```bash
# Navigate to application directory (common pattern)
cd app/

# Pipenv virtual environment management
pipenv shell                    # Activate virtual environment
pipenv install                  # Install dependencies from Pipfile
pipenv install --dev            # Install development dependencies
pipenv --rm                     # Remove virtual environment
```

### Development Commands
```bash
# Application execution
python main.py                  # Run main application
python app.py --help           # Show available commands

# Dependency management
pipenv install package_name     # Install new package
pipenv install --dev pytest    # Install development package
pipenv lock                     # Update Pipfile.lock
```

### Testing
```bash
# Standard pytest execution with proper Python path
PYTHONPATH=. pipenv run pytest                    # Run all tests
PYTHONPATH=.:../ pipenv run pytest               # Run tests with parent path
PYTHONPATH=. pipenv run pytest -v                # Verbose output
PYTHONPATH=. pipenv run pytest tests/file.py     # Run specific test file
PYTHONPATH=. pipenv run pytest tests/file.py::TestClass::test_method -v  # Run specific test

# Alternative execution patterns
pipenv run python -m pytest    # Alternative pytest execution
make test                       # If Makefile is available
make test_verbose              # If Makefile is available
```

### Common Project Patterns
```bash
# Virtual environment workflow
cd app/                         # Enter project directory
pipenv shell                    # Activate environment
python main.py                  # Run application
exit                           # Exit virtual environment

# Clean development cycle
make shell_clean               # Remove environment (if Makefile available)
make install_new               # Fresh install (if Makefile available)
pipenv --rm                    # Manual environment removal
pipenv install                 # Reinstall dependencies
```

### Environment Variables
```bash
# Common environment variable patterns
export VAR_NAME="value"         # Set environment variable
export PYTHONPATH="."          # Set Python path for imports
export API_KEY="your_key"      # API keys and secrets

# Load from .env file (if supported)
pipenv run --env-file .env python main.py
```

## GitHub CLI Integration

The GitHub CLI (`gh`) provides powerful repository management and automation capabilities for Python projects:

### Repository Management
```bash
# Repository operations
gh repo view                    # View current repository details
gh repo clone <repo>           # Clone a repository
gh repo create <name>          # Create new repository
gh repo fork                   # Fork current repository
gh repo view --web            # Open repository in browser
```

### Pull Request Workflow
```bash
# Pull request management
gh pr create                   # Create new pull request
gh pr create --title "Title" --body "Description"  # Create PR with details
gh pr list                     # List pull requests
gh pr list --state=open        # List open pull requests
gh pr view <number>           # View PR details
gh pr view <number> --comments # View PR with comments
gh pr checkout <number>       # Checkout PR locally
gh pr merge <number>          # Merge pull request
```

### Issue Management
```bash
# Issue operations
gh issue create               # Create new issue
gh issue create --title "Bug" --body "Description"  # Create issue with details
gh issue list                 # List issues
gh issue list --state=open    # List open issues
gh issue view <number>        # View issue details
gh issue close <number>       # Close issue
```

### Workflow Management
```bash
# GitHub Actions workflow operations
gh workflow list               # List all workflows
gh workflow view <workflow>    # View workflow details
gh workflow run <workflow>     # Trigger workflow manually
gh workflow enable <workflow>  # Enable workflow
gh workflow disable <workflow> # Disable workflow

# Workflow run monitoring
gh run list                    # List recent workflow runs
gh run list --workflow=<name>  # List runs for specific workflow
gh run list --limit 10         # Limit number of runs shown
gh run view <run-id>          # View specific run details
gh run view <run-id> --log     # View run logs
gh run view <run-id> --log-failed  # View failed run logs
gh run watch <run-id>         # Watch running workflow in real-time
gh run cancel <run-id>        # Cancel running workflow
gh run download <run-id>      # Download run artifacts
```

### Release Management
```bash
# Release operations
gh release create v1.0.0      # Create new release
gh release create v1.0.0 --title "Release v1.0.0" --notes "Release notes"
gh release list                # List all releases
gh release view v1.0.0        # View specific release
gh release upload v1.0.0 dist/*  # Upload files to release
gh release download v1.0.0    # Download release assets
gh release delete v1.0.0      # Delete release
```

### Authentication & Configuration
```bash
# Authentication
gh auth login                 # Login to GitHub
gh auth logout                # Logout from GitHub
gh auth status               # Check authentication status
gh auth refresh              # Refresh authentication token

# Configuration
gh config set editor vim      # Set default editor
gh config set git_protocol https  # Set Git protocol
gh config list               # List current configuration
```

### Advanced Operations
```bash
# Repository collaboration
gh repo set-default <owner/repo>  # Set default repository
gh api repos/:owner/:repo/collaborators  # List collaborators via API
gh api user                   # Get current user info via API

# Bulk operations
gh issue list --json number,title  # Get issues in JSON format
gh pr list --json number,title,state  # Get PRs in JSON format

# Integration with Python projects
gh workflow run python-tests  # Trigger Python test workflow
gh release create v1.0.0 dist/*.whl dist/*.tar.gz  # Release Python packages
```
