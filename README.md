# finerp
UA PE helper for calculate tax reporting


For development
================

Enter the project folder and create a virtual environment for python, execute:

    python3 -m venv .venv3

then activate the virtual environment:

    . .venv3/bin/activate

Install all packages and make migrations:

    pip install pip wheel -U
    make local


Project Folder Structure
========================

repo_root/                     # Project root directory
│── allstatic/                 # Collected static files
│── media/                     # Uploaded media files
│── docker/                    # Docker-related files
│   ├── localdev/server.Dockerfile      # Dockerfile for Django (ASGI + Uvicorn) and Celery worker with Beat
│   ├── localdev/nginx.Dockerfile       # Dockerfile for Nginx reverse proxy
│   ├── localdev/nginx.conf             # Nginx configuration file
│   │── .env                       # Environment variables (not committed to VCS)
│   │── docker-compose.local.yml   # Docker Compose file for local development
│   ├── entrypoint.sh          # Entry script for container initialization
│── requirements/              # Dependency management
│   ├── base.pip               # Base dependencies
│   ├── code-checks.pip        # Linters and code formatting dependencies
│   ├── local.pip              # Local development dependencies
│── sc_backend/                       # Main source code directory
│   ├── djapps/                # All our Django applications
│   │   ├── finops/                 # bstore app
│   ├── djproject/             # Django project configuration (settings, URLs, etc.)
│   ├── manage.py
│── .gitignore
│── Makefile
│── README.md