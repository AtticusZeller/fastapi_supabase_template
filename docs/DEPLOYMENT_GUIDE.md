# Automatic Deployment Configuration Guide

This document explains how to configure and use the automatic deployment system set up in our CI/CD pipeline. The system uses a Docker image promotion-based approach to ensure that the same artifact that was tested is deployed to production.

## Process Overview

Our deployment process follows these steps:

1. **Build and Test**: A Docker image is built from each commit on the `develop` and `main` branches, as well as for each version tag.
2. **Environment Promotion**: Instead of rebuilding the image for each environment, the same image is promoted from one environment to another.
3. **Automatic Deployment**: Once tests pass, deployment happens automatically to the appropriate environments.

## Deployment Rules

- **Development Environment**: All commits on the `develop` branch build a Docker image with the `latest` tag.
- **Staging Environment**: All commits on the `main` branch build a Docker image with the `staging` tag and automatically deploy it to the staging environment.
- **Production Environment**: Any tag creation (semantic version like `v1.2.3`) uses this tag as the image identifier and automatically deploys it to the production environment.

## Required Configuration

### GitHub Secrets

The following secrets must be configured in your GitHub repository settings:

#### Global Secrets
