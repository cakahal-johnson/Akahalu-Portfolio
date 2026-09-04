# Akahalu Portfolio Mobile

Kotlin Multiplatform + Compose Multiplatform mobile application for the Akahalu Portfolio platform.

## Targets

- Android
- iOS

## Architecture

The mobile application consumes the existing Akahalu Portfolio FastAPI backend.

```text
Compose UI
    |
    v
Presentation
    |
    v
Domain
    |
    v
Data
    |
    v
Ktor
    |
    v
FastAPI /api/v1