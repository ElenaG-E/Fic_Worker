# TODO List for Fic_Worker Project Expansion

## Completed Tasks
- [x] Set up basic Flask proxy server (proxy.py) to handle API requests to Google Gemini API
- [x] Create main HTML frontend (index.html) with UI for story generation, PDF upload, AI tools
- [x] Implement PDF processing using PDF.js for client-side text extraction
- [x] Add web worker (api-worker.js) for handling API calls without blocking UI
- [x] Implement story generation with Gemini API integration
- [x] Add story continuation feature
- [x] Implement AI tools: twist generation, character profile, dialogue helper, critique, PDF query, question generation
- [x] Add storybook generation with images and audio (placeholder for TTS)
- [x] Implement export to PDF functionality
- [x] Add PWA features: manifest.json, service worker (sw.js), offline capabilities
- [x] Add dark mode toggle
- [x] Implement local storage for API keys and generated stories
- [x] Add pagination for long stories
- [x] Style with Tailwind CSS and custom CSS

## Pending Tasks - Curated Expansion Plan

### Phase 1: User Authentication System
- [x] Create user authentication models (User model with username, email, password hash)
- [x] Set up SQLite database with SQLAlchemy
- [x] Implement Flask-Login for session management
- [x] Add login/signup routes in Flask backend
- [x] Create login/signup forms in frontend
- [x] Add session-based API key storage (encrypted)
- [x] Update proxy.py to handle authenticated requests
- [x] Add logout functionality
- [x] Test authentication flow

### Phase 2: Database Integration
- [ ] Create database models for stories, user profiles, settings
- [ ] Implement CRUD operations for stories
- [ ] Add story saving/loading from database
- [ ] Migrate localStorage stories to database
- [ ] Add user story history and management
- [ ] Implement story versioning
- [ ] Add database migrations

### Phase 3: Advanced AI Tools
- [ ] Implement story analysis tool (sentiment, themes, pacing)
- [ ] Add character relationship mapping
- [ ] Create plot mapping/visualization
- [ ] Add story consistency checker
- [ ] Implement advanced prompt engineering
- [ ] Add AI-powered story suggestions

### Phase 4: UI/UX Improvements
- [ ] Add multiple theme options (beyond dark/light)
- [ ] Implement smooth animations and transitions
- [ ] Improve responsive design for mobile/tablet
- [ ] Add drag-and-drop for file uploads
- [ ] Implement better loading states and progress indicators
- [ ] Add keyboard shortcuts
- [ ] Improve accessibility (ARIA labels, focus management)

### Phase 5: Backend Enhancements
- [ ] Implement rate limiting for API calls
- [ ] Add caching for frequent requests
- [ ] Improve error handling and logging
- [ ] Add request validation and sanitization
- [ ] Implement background job processing (if needed)
- [ ] Add health check endpoints

### Phase 6: Security Features
- [ ] Encrypt API keys in database
- [ ] Add input validation and sanitization
- [ ] Implement CSRF protection
- [ ] Add secure headers (helmet equivalent for Flask)
- [ ] Implement password strength requirements
- [ ] Add account lockout after failed attempts

### Phase 7: Deployment Setup
- [ ] Create Dockerfile for containerization
- [ ] Add docker-compose for local development
- [ ] Create deployment scripts
- [ ] Add environment configuration
- [ ] Create basic cloud deployment guide (Heroku/AWS)
- [ ] Add production settings

### Phase 8: Testing Framework
- [ ] Set up pytest for backend testing
- [ ] Add unit tests for key functions
- [ ] Implement integration tests for API endpoints
- [ ] Add frontend testing with Jest (if needed)
- [ ] Create test fixtures and mocks

### Phase 9: Documentation
- [ ] Update README.md with setup instructions
- [ ] Add API documentation
- [ ] Create user guide/tutorial
- [ ] Add developer documentation
- [ ] Create deployment guide
- [ ] Add troubleshooting section
