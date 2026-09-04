# Akahalu Portfolio Mobile

Kotlin Multiplatform + Compose Multiplatform mobile application for the Akahalu Portfolio platform.

## Targets

- Android
- iOS

## Architecture

The mobile application consumes the existing Akahalu Portfolio FastAPI backend.

```text
Compose UI
    ↓
Presentation
    ↓
Domain
    ↓
Data
    ↓
Ktor
    ↓
FastAPI /api/v1