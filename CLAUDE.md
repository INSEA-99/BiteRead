# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BiteRead is a mobile application built with React Native and Expo, with a Python FastAPI backend for LangChain integration. The project follows a monorepo structure with two main components:

- **frontend/**: React Native mobile app using Expo and file-based routing
- **langchain-server/**: Python FastAPI server for AI/LangChain functionality

## Development Commands

### Frontend (React Native/Expo)

Navigate to the `frontend/` directory for all frontend commands:

```bash
cd frontend
npm install                 # Install dependencies
npm start                   # Start Expo development server
npm run android            # Run on Android emulator
npm run ios                # Run on iOS simulator
npm run web                # Run web version
npm run lint               # Run ESLint
```

The Expo development server provides options to run on:
- Physical device via Expo Go app
- Android emulator
- iOS simulator
- Web browser

### Backend (Python/FastAPI)

Navigate to the `langchain-server/` directory for backend commands:

```bash
cd langchain-server
python -m venv venv        # Create virtual environment
source venv/bin/activate   # Activate venv (Unix/Mac)
venv\Scripts\activate      # Activate venv (Windows)
pip install -r requirements.txt  # Install dependencies
python main.py             # Run FastAPI server
```

## Architecture

### Frontend Structure

The frontend uses **Expo Router** for file-based routing with the following architecture:

- **app/**: Route definitions and screens (file-based routing)
  - `_layout.tsx`: Root layout with theme provider and navigation setup
  - `(tabs)/`: Tab-based navigation group
    - `_layout.tsx`: Tab navigation configuration
    - `index.tsx`: Home tab screen
    - `explore.tsx`: Explore tab screen
  - `modal.tsx`: Modal screen example

- **components/**: Reusable UI components
  - Themed components (`themed-text.tsx`, `themed-view.tsx`) for dark/light mode support
  - `haptic-tab.tsx`: Tab navigation with haptic feedback
  - `ui/`: Platform-specific UI components (e.g., `icon-symbol.tsx` with iOS variant)

- **constants/theme.ts**: Color schemes and fonts for light/dark modes

- **hooks/**: Custom React hooks
  - `use-color-scheme.ts`: Hook for detecting and managing color scheme
  - `use-theme-color.ts`: Hook for theme-aware colors

**Key patterns:**
- Path alias `@/*` resolves to frontend root directory
- File-based routing: directory structure in `app/` defines routes
- Platform-specific files use `.ios.tsx`, `.android.tsx`, or `.web.ts` extensions
- Theme switching between light and dark modes is built-in

### Backend Structure

The backend uses **FastAPI** with a modular structure:

- **main.py**: FastAPI application entry point with router registration
- **app/**: Application modules
  - `endpoints/`: API route handlers (e.g., `feedback.router`)
  - `models/`: Data models and schemas
  - `services/`: Business logic and service layer

**Key patterns:**
- RESTful API design with FastAPI routers
- Modular endpoint organization by feature
- Separation of concerns: endpoints, models, and services

## Git Commit Conventions

This project follows the **Conventional Commits** specification for clear and consistent commit messages.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (whitespace, formatting, semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvements
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes to build system or external dependencies (npm, pip, etc.)
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files

### Scope (Optional)

Scope provides additional context and should indicate the area of change:

- **frontend**: Changes in the React Native/Expo app
- **backend**: Changes in the FastAPI/LangChain server
- **api**: API endpoint changes
- **ui**: User interface components
- **nav**: Navigation/routing changes
- **theme**: Theme or styling changes
- **deps**: Dependency updates

### Examples

```bash
# Feature addition
feat(frontend): add article reading screen with text-to-speech

# Bug fix
fix(backend): resolve LangChain API timeout issue

# Documentation
docs: update installation instructions in README

# Refactoring
refactor(ui): reorganize themed components for better reusability

# Performance improvement
perf(frontend): optimize image loading with lazy loading

# Dependency update
build(backend): upgrade FastAPI to version 0.109.0
```

### Rules

1. Use imperative mood in the subject line ("add" not "added" or "adds")
2. Don't capitalize the first letter of the subject
3. No period at the end of the subject line
4. Limit subject line to 50 characters for readability
5. Wrap body text at 72 characters for CLI readability
6. Separate subject from body with a blank line
7. Use the body to explain **what** and **why**, not **how**
8. Body can use bullet points for multiple changes
9. Reference issue numbers in the footer when applicable

### Breaking Changes

For breaking changes, add `BREAKING CHANGE:` in the footer or append `!` after the type/scope:

```bash
feat(api)!: change authentication endpoint structure

BREAKING CHANGE: /auth/login endpoint now returns different response format
```

## Development Notes

- Frontend uses TypeScript with strict mode enabled
- React Native version: 0.81.5 with React 19.1.0
- Navigation uses `@react-navigation` with bottom tabs
- Backend is set up for LangChain integration (server currently has minimal endpoints)
- The project appears to be in early development stages with placeholder directories in the backend
