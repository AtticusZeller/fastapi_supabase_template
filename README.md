<p align="center">
  <img src="docs/assets/logo.png" alt="Logo">
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://codecov.io/gh/Atticuszz/fastapi_supabase_template">
    <img src="https://codecov.io/gh/Atticuszz/fastapi_supabase_template/branch/main/graph/badge.svg?token=YOUR_TOKEN" alt="codecov">
  </a>
  <a href="https://github.com/Atticuszz/fastapi_supabase_template/actions">
    <img src="https://github.com/Atticuszz/fastapi_supabase_template/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/Atticuszz/fastapi_supabase_template/releases/">
    <img src="https://img.shields.io/github/release/Atticuszz/fastapi_supabase_template.svg" alt="GitHub release">
  </a>
  <img src="https://img.shields.io/badge/python-3.10|3.11|3.12-blue.svg" alt="Python">
  <a href="https://supabase.com">
    <img src="https://supabase.com/badge-made-with-supabase-dark.svg" alt="Made with Supabase">
  </a>
</p>

# ⚡SupaFast⚡

___
> supabase & fastapi crud template

![supafast.drawio.png](docs/assets/supafast.drawio.png)

## Features 🚀

___

## How to use it



### install python dependencies

cd your repo and install dependencies with [uv](https://github.com/astral-sh/uv), which is an extremely fast Python package and project manager, written in Rust.

```shell
uv sync
```

### install supabase

1. [start your supabase locally](https://supabase.com/docs/guides/local-development/cli/getting-started?queryGroups=platform&platform=linux&queryGroups=access-method&access-method=postgres)

```bash
# brew in linux https://brew.sh/
brew install supabase/tap/supabase
supabase init
supabase start
```

2. set your supabase env

```shell
export SUPABASE_URL=your_supabase_url
export SUPABASE_KEY=your_supabase_key
```


### run

1. run server

```shell
uv run uvicorn app.main:app --reload
```

## Roadmap 🫶

___

- [x] FastAPI backend
  - [ ] Layered Architecture
      for <a href="https://github.com/tiangolo/fastapi" class="external-link" target="_blank">**FastAPI**</a> project
  - [ ] sqlmodel ORM supabase
    - [x] test_pre_start.py
    - [ ] pre_start.py
    - [ ] alembic
    - [ ] crud test
  - [ ] api test

- [ ] Supabase integration
  - [ ] crud supabase-postgresql
  - [ ] websocket with supabase-realtime
  - [ ] curd supabase-storage
  - [ ] supafunc integration
- [ ] deployment
  - [ ] Full **Docker** integration (Docker based).
