# Spotifiologist v2

Don't let your Spotify data go to waste! A modern Python toolkit for managing and enhancing your Spotify library.

## Overview
Spotifiologist helps you take control of your Spotify data by providing tools to backup, analyze, and enhance your music library. Never lose track of your musical journey.

## Development Phases

### Phase 1: Core Infrastructure 🏗️
- [x] Spotify API Integration
  - [x] Authentication and authorization flow (via SpotifyOAuth)
  - [x] Rate limiting and error handling (via Spotipy)
  - [x] Library data models (tracks, albums, playlists)
  - [ ] Library data fetching
    - [x] Tracks and albums
    - [ ] Playlists (in progress)

- [ ] Data Storage Layer
  - Schema design for library entities
  - Efficient storage and retrieval
  - Change tracking and versioning
  - Diff generation for library changes

### Phase 2: Library Backup & Monitoring 💾
- [ ] Library Backup
  - Automated backup of saved items
    - Tracks and albums
    - Artists and playlists
  - Periodic sync (configurable intervals)
  - Backup verification

- [ ] Weekly Library Digest
  - Email-based change notifications
  - Library diff reports
    - New additions
    - Removed items
    - Playlist changes
  - HTML email templates with rich formatting

### Phase 3: Enhanced Features 🎯
- [ ] Advanced Library Management
  - Bulk operations on library items
  - Custom categorization and tagging
  - Export capabilities

- [ ] Smart Features (Future)
  - Automated playlist management
  - Content recommendations
  - Activity tracking and insights

### Maybe Later 🤔
- Activity/listening history tracking
- Streaming statistics
- Genre-based analysis
- Mood tracking

## Future Roadmap 🗺️

### Web Application (v3) 🌐
Future plans include evolving Spotifiologist into a full-featured web application:

- Modern Web Interface
  - Dashboard for library management
  - Visual analytics and insights
  - Interactive playlist management
  - User authentication and profiles

- Architecture Evolution
  - FastAPI backend
  - Modern frontend (React/Next.js)
  - RESTful API design
  - Container-based deployment

## Technical Requirements

### Core Dependencies
- Python 3.11+
- Spotipy (Spotify API client)
- Pydantic (data validation)
- PostgreSQL 15+ (data storage)
- SQLAlchemy + Alembic (ORM & migrations)
- FastAPI-Mail (email notifications)

### Development Tools
- Poetry/Conda (dependency management)
- Ruff & Black (code quality)
- Pytest (testing)
- GitHub Actions (CI/CD)

## Project Structure
```
src/
├── core/           # Business logic and data models
│   ├── models/     # Pydantic models
│   └── services/   # Business logic
├── database/       # Storage layer
│   ├── models/     # Database models
│   └── repos/      # Data access
└── spotify_utils/  # Spotify API integration
    ├── client.py   # API client
    └── auth.py     # Authentication
```

## Getting Started

### Development Setup
1. Clone the repository
2. Create conda environment: `conda create -n spotifiologist python=3.11`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `example.env` to `.env` and configure
5. Run tests: `pytest`

### Configuration
Required environment variables:
```bash
# Spotify Configuration
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/spotifiologist

# Email Configuration (for weekly digests)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
DIGEST_RECIPIENTS=user@example.com
```

## Development Status
🏗️ Phase 1: Core Infrastructure
