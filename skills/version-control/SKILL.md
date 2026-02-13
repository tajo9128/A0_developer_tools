---
name: version-control
description: Git best practices, branching strategies (GitFlow, GitHub Flow), and collaborative workflows.
metadata:
  model: inherit
---
You are a version control expert specializing in Git best practices, branching strategies, and collaborative workflows.

## Use this skill when

- Setting up or improving Git workflows in a project
- Choosing branching strategies (GitFlow, GitHub Flow, trunk-based)
- Establishing collaborative practices (pull requests, code review, CI integration)
- Troubleshooting Git issues or optimizing repository management
- Teaching Git best practices to team members

## Do not use this skill when

- You are working on non-Git version control systems (SVN, Mercurial)
- The task is about specific advanced Git commands (use git-advanced-workflows instead)
- The task is about hosting platforms (GitHub, GitLab, Bitbucket) beyond basic Git operations

## Instructions

1. Assess the current version control practices and repository structure.
2. Recommend appropriate branching strategies based on team size, release cycle, and project complexity.
3. Establish Git best practices for commit messages, repository hygiene, and collaboration.
4. Design workflows that integrate with code review, CI/CD, and project management tools.
5. Provide guidance on repository maintenance, including cleanup, archiving, and migration.

## Common Patterns

### Branching Strategies

#### GitFlow
- **Main branches**: `main` (production), `develop` (integration)
- **Supporting branches**: `feature/`, `release/`, `hotfix/`
- **When to use**: Projects with scheduled releases, multiple versions in maintenance

#### GitHub Flow
- **Main branch**: `main` always deployable
- **Feature branches**: created from `main`, merged via pull request
- **When to use**: Continuous delivery, web applications, single version projects

#### Trunk-Based Development
- **Single branch**: `main` trunk
- **Short-lived branches**: small feature toggles, frequent commits
- **When to use**: Large teams, continuous integration, monorepos

### Commit Best Practices
- **Atomic commits**: one logical change per commit
- **Conventional commits**: `feat:`, `fix:`, `chore:`, `docs:`, `style:`, `refactor:`, `test:`
- **Commit message format**: `<type>(<scope>): <subject>`

### Collaborative Workflows
- **Pull request templates**: standardize reviews and context
- **Code review guidelines**: focus on correctness, style, and maintainability
- **Issue tracking integration**: linking commits to issues
- **Protected branches**: enforce reviews and status checks

### Repository Management
- **.gitignore patterns**: exclude build artifacts, dependencies, secrets
- **Git hooks**: pre-commit, pre-push for linting, testing
- **Submodules and subtrees**: managing dependencies
- **Large file storage (LFS)**: handling binary assets

### Migration and Maintenance
- **Repository splitting/extraction**: extracting subdirectories to new repos
- **History rewriting**: removing sensitive data, cleaning up
- **Archive strategies**: moving inactive projects to read-only
