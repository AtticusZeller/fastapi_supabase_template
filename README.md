# FastAPI Supabase Template

## Environment

### Python

> [uv](https://github.com/astral-sh/uv) is an extremely fast Python package and project manager, written in Rust.

```bash
cd backend
uv sync --all-groups --dev
```

### [Supabase](https://supabase.com/docs/guides/local-development/cli/getting-started?queryGroups=platform&platform=linux&queryGroups=access-method&access-method=postgres)

install supabase-cli

```bash
# brew in linux https://brew.sh/
brew install supabase/tap/supabase
```

launch supabase docker containers

```bash
# under repo root
supabase start
```

> [!NOTE]
>```bash
># Update `.env`
>bash scripts/update-env.sh
>```
> modify the `.env` from the output of `supabase start` or run `supabase status` manually.

## Test

```bash
cd backend
# test connection of db and migration
scripts/pre-start.sh
# unit test
scripts/test.sh
# test connection of db and test code
scripts/tests-start.sh
```

## Docker

> [!note]
> `atticux/fastapi_supabase_template` is your image tag name, remember replace it with yours

build

```bash
cd backend
docker build -t atticux/fastapi_supabase_template .
```

test

```bash
bash scripts/update-env.sh
supabase start
cd backend
docker run --network host \
  --env-file ../.env \
  -it atticux/fastapi_supabase_template:latest \
  bash -c "sh scripts/pre-start.sh && sh scripts/tests-start.sh"
```
