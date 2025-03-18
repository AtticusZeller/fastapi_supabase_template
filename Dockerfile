# Ref: https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/Dockerfile
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Set shell options
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Print logs immediately
# Ref: https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED=1

# Arguments for user creation - avec des valeurs par défaut nulles
ARG USERNAME=""
ARG USER_UID=1000
ARG USER_GID=1000
ARG BUILD_ENV="prod"

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    sudo \
    git \
    curl \
    ca-certificates \
    gpg \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Hadolint
RUN curl -fsSL -o /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64 \
    && chmod +x /usr/local/bin/hadolint

# Set working directory
WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6.4 /uv /uvx /bin/

# Configure UV for system-wide installation in container
ENV UV_SYSTEM_PYTHON=/usr/local/bin/python
ENV UV_CACHE_DIR=/app/backend/.cache/uv
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

# Create cache directory
RUN mkdir -p $UV_CACHE_DIR && \
    chmod -R 777 $UV_CACHE_DIR

# Copy backend files for dependency installation
COPY . .
RUN echo "=== Backend contents ===" && \
    ls -la backend && \
    echo "=== uv.lock contents ===" && \
    cat backend/uv.lock && \
    echo "=== Python path ===" && \
    python -c "import sys; print('\n'.join(sys.path))"

# Install dependencies
WORKDIR /app/backend
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    set -x && \
    # D'abord installer les dépendances
    uv sync --frozen && \
    # Puis installer le projet en mode éditable
    uv pip install --system -e . && \
    echo "=== Installed packages ===" && \
    python -m pip list && \
    echo "=== Site packages location ===" && \
    python -c "import site; print(site.getsitepackages())" && \
    echo "=== Site packages contents ===" && \
    ls -la /usr/local/lib/python3.12/site-packages/

RUN if [ "$BUILD_ENV" = "test" ] || [ "$BUILD_ENV" = "dev" ]; then \
    uv pip install --system -e ".[test]" && \
    uv pip install --system \
    mypy \
    pylint \
    flake8 \
    black \
    isort \
    types-requests \
    types-python-dateutil \
    types-PyYAML \
    ; \
    fi

# Verify installations with more debug
RUN set -x && \
    python -c "import sqlmodel; print(f'SQLModel version: {sqlmodel.__version__}')" && \
    python -c "import alembic; print('Alembic installed successfully')"

# Install Supabase CLI using curl instead of wget
RUN curl -fsSL -o supabase.deb --progress-bar \
    https://github.com/supabase/cli/releases/download/v1.145.4/supabase_1.145.4_linux_amd64.deb \
    && dpkg -i supabase.deb \
    && rm supabase.deb

# Set ownership if in dev mode
RUN if [ -n "$USERNAME" ] && [ "$BUILD_ENV" = "dev" ]; then \
    chown -R $USERNAME:$USERNAME /app; \
    fi

# Si BUILD_ENV est dev, configurer GPG
RUN if [ "$BUILD_ENV" = "dev" ]; then \
    mkdir -p /home/$USERNAME/.gnupg && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME/.gnupg && \
    chmod 700 /home/$USERNAME/.gnupg; \
    fi

# Switch to non-root user if specified
USER ${USERNAME:-root}
WORKDIR /app

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "80"]
# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]
