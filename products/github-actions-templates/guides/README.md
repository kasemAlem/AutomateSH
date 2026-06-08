# The Ultimate GitHub Actions Bundle

Welcome to your new library of battle-tested GitHub Actions!

## How to use these templates:

1. Copy the `.yml` file you want into your project's `.github/workflows/` directory.
2. Review the file and update any placeholders (like your Docker image name or PyPI package name).
3. If the workflow requires secrets (like `ANTHROPIC_API_KEY` or custom deployment keys), add them to your repository's settings: `Settings > Secrets and variables > Actions > New repository secret`.

## Included Templates:

* **Python**: CI pipelines with Ruff & Pytest matrix testing, Trusted PyPI Publishing.
* **Docker**: Buildx caching, GitHub Container Registry pushing, image signing with Cosign.
* **AI Workflows**: Claude AI PR reviewers.

*More templates to be added soon!*
