#!/usr/bin/env bash

uvx --with mkdocs-material \
    --with mkdocs-git-revision-date-localized-plugin \
    --with mkdocs-glightbox \
    --with mkdocs-obsidian-bridge \
    --with mkdocs-publisher \
    --with pymdown-extensions \
    mkdocs serve
