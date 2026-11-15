# PawPass

## Overview
PawPass is a lightweight web platform designed for animal shelters and foster volunteers to easily transfer pet information between shifts, volunteers, fosters, and shelters without relying on emails and Excel sheets. The application is built as a Progressive Web App (PWA) with offline functionality and database persistence, featuring a custom logo and user-friendly interface that facilitates seamless pet care coordination.

Live demo: https://pawpass-kumailr.vercel.app - on mobile, navigation collapses into a hamburger menu.

## Features
- **Pet Profiles**: Create and manage detailed pet information
- **Care Updates**: Log updates about pet care and behavior
- **Shift Checklists**: Track completed care tasks during shifts
- **Image Upload**: Upload and manage pet photos
- **Emergency Flagging**: Mark pets requiring urgent care
- **Progressive Web App**: Works offline and can be installed on devices
- **Accessibility**: Color-blind friendly mode
- **Search Functionality**: Quickly find pets by name

## Architecture
The application follows a modular architecture with the following components:

### Module Boundaries
- **Auth**: Authentication and authorization services
- **Email**: Email processing and notifications
- **AI**: AI integration for pet care recommendations
- **Encryption**: Data security and encryption

### Tech Stack
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **PWA Support**: Service Worker, App Manifest

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/pets` | GET | Retrieve all pets |
| `/api/pets/<id>` | GET | Get a specific pet |
| `/api/pets/<id>/update` | POST | Add an update to a pet |
| `/api/pets/<id>/checklist` | POST | Add a checklist to a pet |

## Integration Patterns
- **Database Integration**: Direct ORM integration with PostgreSQL
- **Authentication**: Session-based authentication for user login, registration, and profile management.
- **PWA**: Cache-first strategy with background sync for offline mode
- **Image Upload**: Multipart form data with server-side processing
- **Search**: Database query pattern with real-time results

## Getting Started
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Set up PostgreSQL database
4. Run the application: `gunicorn --bind 0.0.0.0:5000 main:app`

## Development
- Follow PEP 8 for Python code
- Document all functions and modules
- Write tests for new features
- Commit changes with descriptive messages

## Redesign (Nov 2026)
- Warm, rounded redesign ported from the PawPass 3D redesign: soft daylight palette, orange pass card with gentle 3D tilt and flip (`static/css/pawpass-redesign.css`, `static/js/pawpass-pass.js`).
- The pet profile is a flippable pass. Front: pet identity and pass status. Back: feeding instructions, medical notes, latest update and checklist count from the real record.
- Pass status is derived from the pet's real record only: a pet flagged for emergency care shows "Action needed"; otherwise "Ready at check-in". PawPass does not store vaccination records, so the pass makes no vaccination claim.
- Offline-first: the service worker (`pawpass-v2`) precaches the redesign assets and the home, pet list and add-a-pet pages; a header badge shows live online/offline state.
- CI (`.github/workflows/ci.yml`) runs on every push to main and pull request: it compile-checks the Python, parse-checks every Jinja template, and verifies the service worker only caches files that exist. The backend logic, tests and data model were not changed.
