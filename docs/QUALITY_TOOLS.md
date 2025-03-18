# Code Quality Tools

This document details the code quality tools configured in this project, how they are integrated into our development process, and how to use them effectively.

## SonarCloud

SonarCloud is a continuous automatic code analysis service that detects bugs, vulnerabilities, and code smells in your code.

### Configuration

The project is configured to use SonarCloud via the `sonar-project.properties` file at the project root and the GitHub Actions workflow `.github/workflows/sonarcloud.yml`.

### Monitored Metrics

- **Code Quality**: Identification of code issues such as potential bugs, vulnerabilities, and code smells
- **Test Coverage**: Percentage of code covered by automated tests
- **Code Duplication**: Detection of duplicated code blocks
- **Complexity**: Analysis of cyclomatic and cognitive complexity
- **Technical Debt**: Estimation of time needed to fix all code issues

### Viewing Results

SonarCloud analysis results are available:

1. On the [project's SonarCloud dashboard](https://sonarcloud.io/project/overview?id=acout_fastapi_supabase_template)
2. Directly in Pull Requests via SonarCloud comments
3. Via badges in the project README

### Local Configuration

To configure SonarCloud for your project fork:

1. Create an account on [SonarCloud](https://sonarcloud.io/) and link it to your GitHub account
2. Import your repository into SonarCloud
3. Generate an access token in SonarCloud
4. Add this token as a GitHub secret in your repository with the name `SONAR_TOKEN`
5. Adapt the `sonar-project.properties` file to reflect your organization and project information

## Codecov

Codecov is a tool that allows you to visualize and analyze your project's code coverage.

### Configuration

Codecov is integrated into the main GitHub Actions workflow `.github/workflows/main.yml`. Coverage reports are generated during test execution and sent to Codecov.

### Features

- **Coverage Visualization**: Graphical interface to explore code coverage
- **Coverage Evolution**: Track coverage changes over time
- **Pull Request Analysis**: Automatic verification of coverage changes in PRs
- **Badges**: Coverage badges for your README

### Local Configuration

To configure Codecov for your fork:

1. Create an account on [Codecov](https://codecov.io/) and link it to your GitHub account
2. Import your repository into Codecov
3. Generate a Codecov token if needed
4. Add this token as a GitHub secret with the name `CODECOV_TOKEN`

## Local Coverage Report Generation

You can generate coverage reports locally to check results before pushing your changes:
