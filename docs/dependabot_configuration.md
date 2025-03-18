# Dependabot Configuration

## Overview

This project uses Dependabot to automate dependency management and keep our packages up to date while prioritizing security. This documentation explains our configuration and associated best practices.

## Configuration

Our Dependabot configuration manages three distinct ecosystems:

1. **GitHub Actions** - Updates for actions in our CI/CD workflows
2. **Python (pip)** - Python dependencies of our application
3. **Docker** - Docker image updates

### Frequency and Scheduling

All updates are scheduled for **Monday at 9:00 AM (Paris time)** to minimize disruption during the work week. This scheduling allows the team to process dependency PRs at the start of the week.

### Smart Grouping

To reduce noise and review workload, we have configured groupings:

- **GitHub Actions**: All action updates are grouped together
- **Python**: Separation between production and development dependencies
  - Grouping of minor and patch updates
  - Individual handling of major updates that may introduce incompatibilities
- **Docker**: All Docker updates are grouped together

### Pull Request Automation

We have implemented an automation workflow for Dependabot:

- **Automatic approval** for minor and patch updates
- **Automatic merge** for GitHub Actions updates
- **Manual review required** for major updates

## Best Practices

### Handling Dependabot PRs

1. **Minor/patch updates**: Generally safe, they are automatically approved and merged
2. **Major updates**: Carefully review changes and release notes before merging
3. **Security vulnerabilities**: Absolute priority, to be addressed as soon as possible

### Conflict Resolution

In case of conflicts in Dependabot PRs:

1. Check changes in each affected file
2. Resolve conflicts manually based on project needs
3. Run complete test suite before approving

### Ignoring Dependencies

In some cases, it may be necessary to temporarily ignore updates for a specific dependency. To do this:

1. Uncomment the `ignore` section in `.github/dependabot.yml`
2. Add the name of the dependency to ignore
3. Add a comment explaining why this dependency is ignored and until when

## Troubleshooting

### Failed Dependabot PRs

If tests fail on a Dependabot PR:

1. Check if the update is compatible with other dependencies
2. Consult release notes to identify important changes
3. Update code or tests if necessary to adapt to new versions

### Too Many Open PRs

If the number of Dependabot PRs becomes difficult to manage:

1. Adjust check frequency from `weekly` to `monthly`
2. Reduce the `open-pull-requests-limit` value
3. Consider grouping more updates together

## Additional Resources

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates)
- [Advanced Dependabot Configuration](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories/about-coordinated-disclosure-of-security-vulnerabilities)
