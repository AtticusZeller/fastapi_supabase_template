# Ref: https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/Dockerfile
# Étape de base commune
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye as base

# Set shell options
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Build arguments avec des valeurs par défaut
ARG BUILD_ENV=prod
ARG USERNAME=appuser
ARG USER_UID=1000
ARG USER_GID=1000

# Variables d'environnement communes
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    UV_SYSTEM_PYTHON=/usr/local/bin/python \
    UV_CACHE_DIR=/app/backend/.cache/uv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

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

# Copy backend files for dependency installation
COPY . .

# Installation des dépendances de base
WORKDIR /app/backend
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv sync --frozen && \
    uv pip install --system -e .

# Stage de développement
FROM base as development
ARG USERNAME
ARG USER_UID
ARG USER_GID

# Installation des outils de développement
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv pip install --system -e ".[test]" && \
    uv pip install --system debugpy ipython

# Install Supabase CLI using curl instead of wget
RUN curl -fsSL -o supabase.deb --progress-bar \
    https://github.com/supabase/cli/releases/download/v1.145.4/supabase_1.145.4_linux_amd64.deb \
    && dpkg -i supabase.deb \
    && rm supabase.deb

    # Configuration de l'environnement de développement
ENV ENVIRONMENT=development \
APP_MODE=api \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONBREAKPOINT=ipdb.set_trace

# Création de l'utilisateur de développement
RUN if [ -n "$USERNAME" ]; then \
        groupadd --gid $USER_GID $USERNAME && \
        useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
        echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
        chmod 0440 /etc/sudoers.d/$USERNAME; \
    fi

# Configuration Git et GPG pour le développement
RUN if [ -n "$USERNAME" ]; then \
        mkdir -p /home/$USERNAME/.gnupg && \
        chown -R $USERNAME:$USERNAME /home/$USERNAME/.gnupg && \
        chmod 700 /home/$USERNAME/.gnupg; \
    fi

USER ${USERNAME}

# Stage de staging
FROM base as staging

# Configuration de l'environnement staging
ENV ENVIRONMENT=staging \
    APP_MODE=api \
    PORT=10000 \
    HOST=0.0.0.0 \
    AUTORUN_MIGRATIONS=true

# Création de l'utilisateur système pour staging
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 appuser && \
    mkdir -p /app/backend/alembic/versions && \
    chown -R appuser:appuser /app

# Configuration des permissions
RUN mkdir -p /app/backend/logs && \
    chmod -R 755 /app/backend && \
    chown -R appuser:appuser /app/backend/logs

USER appuser

# Stage final - Approche avec conditionnels plutôt que variables
FROM development as final-development
COPY --chown=${USERNAME}:${USERNAME} scripts/entrypoint.sh /app/scripts/
RUN chmod +x /app/scripts/entrypoint.sh
WORKDIR /app
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

FROM staging as final-staging
COPY --chown=appuser:appuser scripts/entrypoint.sh /app/scripts/
RUN chmod +x /app/scripts/entrypoint.sh
WORKDIR /app
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Stage final par défaut (production)
FROM base as final-prod
USER appuser
COPY --chown=appuser:appuser scripts/entrypoint.sh /app/scripts/
RUN chmod +x /app/scripts/entrypoint.sh
WORKDIR /app
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Stage final (sélection par défaut)
# hadolint ignore=DL3006
FROM final-${BUILD_ENV} as final
