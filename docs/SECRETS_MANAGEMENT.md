# Secrets Management

This document explains how to manage secrets in the project, particularly for CI/CD testing.

## General Principles

1. **Never version secrets**: `.env`, `.env.test`, etc. files are excluded from version control via `.gitignore`.
2. **Use GitHub secrets**: For CI/CD, all secrets are stored in GitHub Actions.
3. **Consistent naming**: CI test secrets have the `_TEST` suffix.

## Local Configuration

### `.env.test` File

Create a `.env.test` file at the project root with the following variables:
