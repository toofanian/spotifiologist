from setuptools import setup, find_packages

setup(
    name="spotifiologist",
    version="2.0.0",
    description="Spotify library backup and monitoring tool",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9,<3.12",
    install_requires=[
        # Core Dependencies
        "spotipy>=2.19.0,<2.20.0",  # Spotify API client (pinned for stability)
        "pydantic>=1.10.0,<2.0.0",  # Data validation (v1 for compatibility)
        "python-dotenv>=1.0.0",     # Environment management
        "loguru>=0.7.2",            # Better logging
        "attrs>=21.4.0"             # Required by spotipy
        
        # Storage & Data Management
        "sqlalchemy>=2.0.27",      # Database ORM
        "alembic>=1.13.1",         # Database migrations
        "asyncpg>=0.29.0",         # Async PostgreSQL driver
    ],
    extras_require={
        "notifications": [
            # Email & Notifications
            "fastapi-mail>=1.4.1",     # Email sending with async support
            "jinja2>=3.1.3",           # HTML email templates
            "aiosmtplib>=3.0.1",       # Async SMTP client
        ],
        "dev": [
            # Development Tools
            "pytest>=8.0.0",           # Testing
            "black>=24.1.1",           # Code formatting
            "ruff>=0.2.1",             # Fast Python linter
            "pytest-cov>=4.1.0",       # Test coverage
            "pytest-asyncio>=0.23.5",  # Async test support
        ],
        "web": [
            # Web Application Dependencies
            "fastapi>=0.110.0",        # Web framework
            "uvicorn>=0.27.1",         # ASGI server
            "python-jose>=3.3.0",      # JWT authentication
            "passlib>=1.7.4",          # Password hashing
            "python-multipart>=0.0.9",  # Form data parsing
        ]
    }
)
