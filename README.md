# CoffeeBliss — backend (paused)

The API for [Dad's Coffee Shop](https://github.com/SwapnanilBala/Dad-s-Coffee-Shop), a restaurant ordering storefront.

> **Status: paused.** The FastAPI routes were removed and the router modules are placeholders.
> The storefront currently runs frontend-only. What remains is part of the data layer the API
> was built on. It doesn't run as-is: `app/models.py` was cut mid-removal and doesn't parse.

## What's here

| Path | Contains |
| --- | --- |
| `app/database.py` | Async SQLAlchemy engine and session for Neon Postgres (`asyncpg`, SSL) |
| `app/models.py` | Partial table definitions: order items, newsletter subscribers, reward balances and transactions |
| `app/schemas.py` | Pydantic schemas for auth, menu, orders, newsletter and rewards |
| `app/routers/` | Placeholders for `auth`, `menu`, `orders`, `newsletter` and `rewards` |

## Configuration

Copy `.env.example` to `.env` and fill in:

- `DATABASE_URL`: a Neon connection string in the form `postgresql+asyncpg://user:password@host/dbname`
- `SECRET_KEY`: generate one with `python -c "import secrets; print(secrets.token_hex(32))"`

`.env` is git-ignored. Never commit it.

## Stack

Python · FastAPI · SQLAlchemy (async) · asyncpg · Neon Postgres
