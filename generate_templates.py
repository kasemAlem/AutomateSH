import os
from pathlib import Path

BASE_DIR = Path("products/github-actions-templates")

templates = {
    "python/python-ci.yml": """name: Python CI Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install ruff pytest
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Lint with Ruff
      run: |
        ruff check .
    - name: Test with pytest
      run: |
        pytest tests/
""",
    "python/pypi-publish.yml": """name: Publish to PyPI
on:
  release:
    types: [published]

jobs:
  pypi-publish:
    name: Upload release to PyPI
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/your-package-name
    permissions:
      id-token: write  # IMPORTANT: this permission is mandatory for trusted publishing
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.x"
    - name: Install pypa/build
      run: python -m pip install build
    - name: Build a binary wheel and a source tarball
      run: python -m build
    - name: Publish package distributions to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
""",
    "docker/docker-build-push.yml": """name: Docker Build & Push
on:
  push:
    branches: [ "main" ]
    tags: [ 'v*.*.*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install cosign
        if: github.event_name != 'pull_request'
        uses: sigstore/cosign-installer@v3.5.0

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log into registry ${{ env.REGISTRY }}
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push Docker image
        id: build-and-push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
""",
    "ai/claude-pr-reviewer.yml": """name: AI PR Reviewer
on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install AI Reviewer
        run: pip install some-ai-reviewer-tool
      - name: Run AI Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ai-reviewer --target $GITHUB_SHA
""",
    "guides/README.md": """# The Ultimate GitHub Actions Bundle

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
""",
    "GUMROAD_MARKETING_COPY.md": """# The Ultimate GitHub Actions Template Bundle

Stop wasting hours trying to figure out YAML syntax, caching strategies, and permissions. 

I've put together the ultimate bundle of **plug-and-play GitHub Actions templates** that you can copy, paste, and use immediately to supercharge your CI/CD pipelines.

### What's Inside?
✅ **Python Workflows**: Matrix testing, Ruff linting, Pytest, and passwordless PyPI publishing.
✅ **Docker Workflows**: Multi-architecture builds, Buildx Layer Caching, and GHCR publishing.
✅ **AI Workflows**: Automated AI Pull Request reviewers.
✅ **Best Practices**: Minimal permissions, fast caching, and modern action versions.

### Why Buy This?
- **Save Time**: Skip the documentation reading phase.
- **Save Money**: Faster builds = lower GitHub Actions minutes.
- **Secure**: Uses OpenID Connect (OIDC) instead of hardcoded secrets wherever possible.

Buy once, use forever in unlimited projects.
"""
}

for filepath, content in templates.items():
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Generated templates successfully.")
