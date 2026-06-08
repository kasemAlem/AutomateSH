import os
import shutil
from pathlib import Path

import structlog
from langchain_core.messages import SystemMessage, HumanMessage
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from app.config import get_settings
from providers.factory import get_provider

logger = structlog.get_logger(__name__)

# Let's generate 10 high-value templates for the first version
TEMPLATES_TO_GENERATE = [
    ("python-pytest-matrix.yml", "Python package testing across multiple Python versions (3.10, 3.11, 3.12) using Pytest and Poetry."),
    ("docker-multiarch-publish.yml", "Build and push multi-architecture Docker images (amd64, arm64) to Docker Hub using buildx."),
    ("stale-pr-closer.yml", "Automatically mark PRs and Issues as stale after 30 days of inactivity, and close them after 7 more days."),
    ("node-ci-cd-aws.yml", "Node.js CI/CD pipeline that runs Jest tests and deploys to AWS ECS on merge to main."),
    ("rust-cargo-cache.yml", "Rust CI pipeline with aggressive Cargo caching to speed up compilation times."),
    ("auto-labeler.yml", "Automatically label PRs based on the paths of the files changed (e.g., frontend, backend, docs)."),
    ("terraform-plan-apply.yml", "Terraform workflow that posts a Plan as a PR comment, and Applies on merge to main."),
    ("dependabot-auto-merge.yml", "Automatically approve and merge Dependabot PRs if they are minor/patch updates and tests pass."),
    ("go-lint-test.yml", "Go (Golang) pipeline running golangci-lint and 'go test' with race detector enabled."),
    ("playwright-e2e.yml", "End-to-End testing pipeline using Playwright, uploading HTML test reports as GitHub Artifacts on failure.")
]

SYSTEM_PROMPT = """You are a DevOps expert and GitHub Actions specialist.
Your task is to generate a production-ready, perfectly formatted GitHub Actions YAML file for the exact use case requested.
Rules:
1. ONLY output the YAML code. Do not wrap it in ```yaml markdown tags. Just pure YAML.
2. Ensure you use modern versions of actions (e.g. actions/checkout@v4).
3. Include helpful comments explaining key parts of the workflow.
4. Ensure it is syntactically valid YAML.
"""

README_PROMPT = """You are a technical writer. I am creating a digital product bundle called "Automate.sh Premium GitHub Actions Templates".
I have generated YAML files for the following use cases:
{use_cases}

Write a professional README.md for this bundle.
It should include:
1. A catchy title and introductory paragraph thanking them for their purchase.
2. A table of contents listing the templates.
3. Instructions on how to use these templates (e.g., place them in .github/workflows/).
4. A brief description of what each template does.
"""

def generate_digital_product():
    """Generates the GitHub Actions digital product bundle."""
    settings = get_settings()
    output_dir = Path(settings.output_dir) / "products" / "github_actions_templates"
    
    # Clean and recreate directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    provider = get_provider()
    llm = provider.get_llm()
    
    # 1. Generate YAML files
    from rich.console import Console
    console = Console()
    
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold blue]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        
        main_task = progress.add_task("Generating 10 premium GitHub Actions templates...", total=len(TEMPLATES_TO_GENERATE))
        
        for filename, description in TEMPLATES_TO_GENERATE:
            logger.info(f"Generating template: {filename}")
            
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"Write a GitHub Actions workflow for: {description}")
            ]
            
            response = llm.invoke(messages)
            
            # Clean output just in case the LLM included markdown blocks
            content = response.content.strip()
            if content.startswith("```yaml"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            file_path = output_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            progress.advance(main_task)
            
        # 2. Generate README
        readme_task = progress.add_task("Writing instruction manual (README.md)...", total=1)
        use_cases_str = "\n".join([f"- {fn}: {desc}" for fn, desc in TEMPLATES_TO_GENERATE])
        
        readme_messages = [
            HumanMessage(content=README_PROMPT.format(use_cases=use_cases_str))
        ]
        readme_response = llm.invoke(readme_messages)
        
        with open(output_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_response.content)
            
        progress.advance(readme_task)
        
        # 3. Zip it up!
        zip_task = progress.add_task("Packaging bundle into .zip file...", total=1)
        zip_base_path = Path(settings.output_dir) / "10-github-actions-templates"
        shutil.make_archive(str(zip_base_path), 'zip', output_dir)
        progress.advance(zip_task)
        
    final_zip_path = str(zip_base_path) + ".zip"
    logger.info(f"Successfully generated digital product bundle at: {final_zip_path}")
    return final_zip_path
