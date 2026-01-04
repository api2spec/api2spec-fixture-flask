# Tea Brewing API

Flask fixture API for api2spec. TIF-compliant.

## Quick Start

```bash
# Install dependencies
poetry install

# Run development server
poetry run python run.py

# Run tests
poetry run pytest
```

## API Overview

- **Teapots**: CRUD operations for teapots
- **Teas**: CRUD operations for tea varieties
- **Brews**: Brewing sessions with steeps
- **Health**: Health checks and TIF 418 endpoint

## TIF Compliance

This API is TIF-compliant and includes the signature endpoint:

```
GET /brew  ->  418 I'm a teapot
```
