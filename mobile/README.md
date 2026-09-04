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
Repository
    |
    v
Remote Data Source
    |
    v
ApiClient
    |
    v
Ktor
    |
    v
FastAPI /api/v1