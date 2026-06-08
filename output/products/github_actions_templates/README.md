# Automate.sh Premium GitHub Actions Templates

Thank you for purchasing **Automate.sh Premium GitHub Actions Templates**! You've just unlocked a powerful collection of battle-tested CI/CD workflows designed to accelerate your development pipeline, enforce quality standards, and automate repetitive tasks. Whether you're shipping Python packages, deploying Node.js microservices, or managing infrastructure as code, these templates will save you hours of configuration and debugging.

---

## Table of Contents

1. [Python Pytest Matrix](#1-python-pytest-matrix)
2. [Docker Multi-Architecture Publish](#2-docker-multi-architecture-publish)
3. [Stale PR & Issue Closer](#3-stale-pr--issue-closer)
4. [Node.js CI/CD to AWS ECS](#4-nodejs-cicd-to-aws-ecs)
5. [Rust Cargo Cache](#5-rust-cargo-cache)
6. [Auto Labeler](#6-auto-labeler)
7. [Terraform Plan & Apply](#7-terraform-plan--apply)
8. [Dependabot Auto-Merge](#8-dependabot-auto-merge)
9. [Go Lint & Test](#9-go-lint--test)
10. [Playwright E2E Tests](#10-playwright-e2e-tests)

---

## How to Use These Templates

1. **Locate your repository's workflow directory**  
   All GitHub Actions workflows must reside in the `.github/workflows/` folder at the root of your repository. If this folder doesn't exist, create it.

2. **Copy the desired template**  
   Place the YAML file(s) from your purchased bundle into `.github/workflows/`. For example:
   ```
   your-repo/
   └── .github/
       └── workflows/
           ├── python-pytest-matrix.yml
           ├── docker-multiarch-publish.yml
           └── ...
   ```

3. **Customize environment variables and secrets**  
   Each template includes placeholder values (e.g., `DOCKER_USERNAME`, `AWS_REGION`, `TERRAFORM_STATE_BUCKET`). Replace these with your own values. Sensitive data should be stored as [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).

4. **Commit and push**  
   Once your workflow files are in place, push the changes to your repository. GitHub will automatically detect the new workflows and run them on the configured triggers.

5. **Monitor workflow runs**  
   Navigate to the **Actions** tab in your GitHub repository to view execution logs, debug failures, and verify successful runs.

---

## Template Descriptions

### 1. Python Pytest Matrix
**File:** `python-pytest-matrix.yml`  
Runs Python package tests across multiple Python versions (3.10, 3.11, 3.12) using **Pytest** and **Poetry**. The matrix strategy ensures your code is compatible with all supported Python releases. Ideal for libraries, CLI tools, or any Python project.

### 2. Docker Multi-Architecture Publish
**File:** `docker-multiarch-publish.yml`  
Builds and pushes multi-architecture Docker images (amd64, arm64) to Docker Hub using **buildx**. Automatically tags images with the branch name and `latest` for main branch pushes. Perfect for containerized applications targeting diverse hardware.

### 3. Stale PR & Issue Closer
**File:** `stale-pr-closer.yml`  
Automatically marks pull requests and issues as **stale** after 30 days of inactivity, then closes them after an additional 7 days. Keeps your repository clean and focused on active work. Excludes labels like `pinned` or `security`.

### 4. Node.js CI/CD to AWS ECS
**File:** `node-ci-cd-aws.yml`  
Full CI/CD pipeline for Node.js applications: runs **Jest** tests on every push, then deploys to **AWS ECS** (Fargate or EC2) when code is merged to `main`. Includes steps for building a Docker image, pushing to ECR, and updating the ECS service.

### 5. Rust Cargo Cache
**File:** `rust-cargo-cache.yml`  
Optimized Rust CI pipeline with aggressive **Cargo caching** to dramatically reduce compilation times. Uses `Swatinem/rust-cache` for dependency caching and runs `cargo build` and `cargo test`. Essential for Rust projects with large dependency trees.

### 6. Auto Labeler
**File:** `auto-labeler.yml`  
Automatically labels pull requests based on the paths of changed files. For example, changes to `frontend/` add the `frontend` label, `backend/` adds `backend`, and `docs/` adds `docs`. Simplifies triage and helps organize PRs by scope.

### 7. Terraform Plan & Apply
**File:** `terraform-plan-apply.yml`  
Terraform workflow that posts an execution **plan** as a PR comment, then **applies** the plan when the PR is merged to `main`. Supports remote state backends (e.g., S3) and includes formatting validation. Keeps infrastructure changes transparent and reviewable.

### 8. Dependabot Auto-Merge
**File:** `dependabot-auto-merge.yml`  
Automatically approves and merges **Dependabot** pull requests for minor and patch updates—but only after all required CI checks pass. Reduces manual overhead while ensuring dependency updates don't break your build.

### 9. Go Lint & Test
**File:** `go-lint-test.yml`  
Go (Golang) pipeline that runs **golangci-lint** for static analysis and `go test -race` with the race detector enabled. Ensures code quality and catches data races early. Compatible with Go modules and works across multiple Go versions.

### 10. Playwright E2E Tests
**File:** `playwright-e2e.yml`  
End-to-end testing pipeline using **Playwright**. Runs tests across Chromium, Firefox, and WebKit. On failure, uploads comprehensive HTML test reports as GitHub Artifacts for debugging. Ideal for web applications requiring cross-browser validation.

---

*Happy automating!*  
— The Automate.sh Team