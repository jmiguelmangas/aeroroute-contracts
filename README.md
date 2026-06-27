# aeroroute-contracts

## OpenAPI

`openapi/aeroroute-v1.json` is generated from the FastAPI application and is
the source used by `aeroroute-web` to generate its TypeScript schema. Regenerate
the web types with `pnpm generate:api` after a compatible contract update.

## Commands

Use `make check` to validate and test all contract documents. `make build`
creates the versioned ZIP release artifact under `dist/`.

Versioned language-neutral schemas shared by API, MLX, training, web, and
platform integration. This repository contains no business logic.
