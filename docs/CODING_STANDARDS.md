# Coding Standards

This document defines the coding standards for the Insperio Labs project. These standards are automatically enforced through linting and formatting tools configured in the project.

## Table of Contents

- [General Principles](#general-principles)
- [Python Code Style](#python-code-style)
- [Documentation](#documentation)
- [Tests](#tests)
- [Security](#security)
- [Automatic Enforcement Tools](#automatic-enforcement-tools)

## General Principles

### Readability and Maintainability

- Prefer readability over conciseness or performance, unless justified.
- Write code that can be easily understood by other developers.
- Avoid overly complex or obscure constructs.

### Simplicity

- Follow the KISS principle (Keep It Simple, Stupid).
- Avoid over-engineering.
- Break down complex problems into simpler components.

### Consistency

- Follow existing project conventions.
- Be consistent in naming, structure, and style.

## Python Code Style

### Formatting

- We use **Ruff** as our code formatter, configured to follow a style close to Black.
- Indentation: 4 spaces (no tabs).
- Maximum line length: 88 characters.
- Use blank lines to separate logical sections of code.

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `UserProfile`, `DatabaseManager`)
- **Functions, methods, variables**: `snake_case` (e.g., `get_user_data`, `db_connection`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`, `API_VERSION`)
- **Modules/packages**: `snake_case` (e.g., `user_authentication`, `data_models`)
- **Function arguments and local variables**: `snake_case`
- **Private variables and methods**: start with `_` (e.g., `_internal_cache`)

### Imports

- Organize imports by groups:
  1. Python standard library
  2. Third-party libraries
  3. Project imports
- Within each group, imports should be alphabetically ordered.
- Prefer absolute imports over relative imports.

Example:
