"""
Automate.sh Content Engine — CLI
Run: python cli.py [COMMAND] [OPTIONS]
"""

from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from app.logger import setup_logging
from database.connection import init_db, get_session
from database.models import Category, Status, Topic

console = Console()

BANNER = """[bold cyan]
  █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗███████╗   ███████╗██╗  ██╗
 ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝   ██╔════╝██║  ██║
 ███████║██║   ██║   ██║   ██║   ██║██╔████╔██║███████║   ██║   █████╗     ███████╗███████║
 ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝     ╚════██║██╔══██║
 ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ███████╗██╗███████║██║  ██║
 ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝[/]
[dim]           🤖 AI Content Engine for Developers | v1.0[/]
"""


@click.group()
@click.version_option(version="1.0.0", prog_name="automate-sh")
def cli():
    """🤖 Automate.sh — AI-powered content generation engine for developers."""
    setup_logging()
    init_db()


# ── GENERATE ──────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--topic", "-t", required=True, help="Content topic to generate (e.g. 'GitHub Actions Cache')")
@click.option("--audience", "-a", default="developers", show_default=True, help="Target audience")
@click.option(
    "--category", "-c",
    type=click.Choice(["AI_CODING", "LINUX", "GITHUB_ACTIONS"], case_sensitive=False),
    default="AI_CODING",
    show_default=True,
    help="Content category for database",
)
@click.option("--dry-run", is_flag=True, help="Generate content but do not save to database")
@click.option("--with-audio", "-w", is_flag=True, help="Generate TTS audio from the script")
@click.option("--composite", "-v", is_flag=True, help="Composite final MP4 video")
@click.option("--publish-tiktok", is_flag=True, help="Publish the final video to TikTok via Composio")
def generate(topic: str, audience: str, category: str, dry_run: bool, with_audio: bool, composite: bool, publish_tiktok: bool):
    """Generate complete video content for a single TOPIC."""
    console.print(BANNER)

    if dry_run:
        console.print("[yellow]⚠  Dry-run mode — results will NOT be saved to database[/]\n")

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold blue]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        stages = [
            ("🔍 Researching topic...", "research"),
            ("✍️  Writing script...", "script"),
            ("💻 Generating code...", "code"),
            ("📢 Creating titles...", "titles"),
            ("🖼️  Thumbnail text...", "thumbnail"),
            ("🏷️  Generating hashtags...", "hashtags"),
            ("📝 Writing description...", "description"),
            ("✅ Quality review...", "quality"),
            ("📁 Exporting markdown...", "export"),
        ]

        task = progress.add_task(stages[0][0], total=len(stages))
        result = None

        try:
            from engine.graph import run_pipeline

            # We run the pipeline as a single call; progress updates are cosmetic
            progress.update(task, description=f"[bold yellow]{stages[0][0]}")

            result = run_pipeline(topic=topic, audience=audience, generate_audio=with_audio, generate_video=composite, publish_tiktok=publish_tiktok)

            # Advance through stages visually
            for desc, _ in stages[1:]:
                progress.update(task, description=f"[bold yellow]{desc}", advance=1)

            progress.update(task, description="[bold green]✅ Complete!", advance=1)

        except Exception as exc:
            console.print(f"\n[bold red]❌ Pipeline error: {exc}[/]")
            raise click.Abort() from exc

    if result is None:
        console.print("[red]No result produced.[/]")
        return

    # ── Display Results ───────────────────────────────────────
    console.print()
    score = result.get("quality_score", 0)
    score_color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
    score_icon = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"

    console.print(Panel(
        f"[bold white]{result['selected_title']}[/]\n\n"
        f"  [dim]Topic:[/]         {result['normalized_topic']}\n"
        f"  [dim]Quality Score:[/] [{score_color}]{score_icon} {score}/10[/]\n"
        f"  [dim]Script Words:[/]  {len(result['script'].split())}\n"
        f"  [dim]Hashtags:[/]      {len(result.get('hashtags', []))}\n"
        f"  [dim]Retries:[/]       {result.get('retry_count', 0)}\n"
        f"  [dim]Output:[/]        [cyan]{result['markdown_path']}[/]",
        title="[bold green]✅ Content Generated[/]",
        border_style="green",
        padding=(1, 2),
    ))

    # Script preview
    script = result["script"]
    preview = script[:350] + "..." if len(script) > 350 else script
    console.print(Panel(
        f"[italic]{preview}[/]",
        title="[bold blue]📜 Script Preview[/]",
        border_style="blue",
        padding=(1, 2),
    ))

    # Titles
    titles_text = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(result.get("titles", [])))
    console.print(Panel(
        titles_text,
        title="[bold yellow]📢 Title Options[/]",
        border_style="yellow",
        padding=(1, 2),
    ))

    # Hashtags
    tags = " ".join(result.get("hashtags", [])[:10])
    console.print(Panel(
        f"[cyan]{tags}[/]",
        title="[bold magenta]🏷️  Hashtags (first 10)[/]",
        border_style="magenta",
        padding=(0, 2),
    ))

    # Save to DB
    if not dry_run:
        with get_session() as session:
            record = Topic(
                title=result["selected_title"],
                category=Category[category.upper()],
                status=Status.GENERATED,
                markdown_path=result["markdown_path"],
                quality_score=result.get("quality_score"),
            )
            session.add(record)
        console.print("\n[green]💾 Saved to database[/]")

    console.print(f"\n[bold green]📁 Output Files:[/] [link={result['markdown_path']}][cyan]{result['markdown_path']}[/][/] (and accompanying video assets)\n")


# ── BATCH ─────────────────────────────────────────────────────────────────────


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--audience", "-a", default="developers", show_default=True, help="Target audience")
@click.option(
    "--category", "-c",
    type=click.Choice(["AI_CODING", "LINUX", "GITHUB_ACTIONS"], case_sensitive=False),
    default="AI_CODING",
    show_default=True,
)
@click.option("--with-audio", "-w", is_flag=True, help="Generate TTS audio from the scripts")
@click.option("--composite", "-v", is_flag=True, help="Composite final MP4 video")
@click.option("--publish-tiktok", is_flag=True, help="Publish the final videos to TikTok via Composio")
def batch(file: Path, audience: str, category: str, with_audio: bool, composite: bool, publish_tiktok: bool):
    """Generate content for multiple topics from a FILE (one topic per line)."""
    console.print(BANNER)

    raw_lines = file.read_text(encoding="utf-8").splitlines()
    topics = [
        line.strip()
        for line in raw_lines
        if line.strip() and not line.strip().startswith("#")
    ]

    if not topics:
        console.print("[yellow]⚠  No topics found. Use one topic per line. Lines starting with # are comments.[/]")
        return

    console.print(f"[bold]Found [cyan]{len(topics)}[/cyan] topics in [cyan]{file.name}[/cyan][/]\n")

    from engine.graph import run_pipeline

    results: list[dict] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        overall = progress.add_task("Processing...", total=len(topics))

        for i, topic in enumerate(topics, 1):
            progress.update(overall, description=f"[{i}/{len(topics)}] {topic[:45]}...")
            try:
                result = run_pipeline(topic=topic, audience=audience, generate_audio=with_audio, generate_video=composite, publish_tiktok=publish_tiktok)
                results.append({
                    "topic": topic,
                    "status": "✅",
                    "score": result.get("quality_score", "?"),
                    "path": result["markdown_path"],
                })
                console.print(f"\n[bold green]✅ Success![/] Topic processed and video assets generated.")
                console.print(f"[dim]Output saved to:[/] {result['markdown_path']} (and accompanying .txt/.md files)")
                with get_session() as session:
                    session.add(Topic(
                        title=result["selected_title"],
                        category=Category[category.upper()],
                        status=Status.GENERATED,
                        markdown_path=result["markdown_path"],
                        quality_score=result.get("quality_score"),
                    ))
            except Exception as exc:
                results.append({"topic": topic, "status": "❌", "score": "-", "path": str(exc)[:60]})
            progress.advance(overall)

    # Results table
    table = Table(title="📊 Batch Results", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Topic", max_width=38)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Score", justify="center", width=7)
    table.add_column("Output / Error", max_width=42)

    for i, r in enumerate(results, 1):
        table.add_row(
            str(i),
            r["topic"][:38],
            r["status"],
            str(r["score"]),
            r["path"][:42],
        )

    console.print()
    console.print(table)

    success = sum(1 for r in results if r["status"] == "✅")
    console.print(f"\n[bold]Result: [green]{success}[/green] / {len(topics)} succeeded[/]\n")


# ── HISTORY ───────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--limit", "-n", default=20, show_default=True, help="Number of records to show")
@click.option(
    "--status", "-s",
    type=click.Choice(["TODO", "GENERATED", "RECORDED", "PUBLISHED"], case_sensitive=False),
    help="Filter by production status",
)
@click.option(
    "--category", "-c",
    type=click.Choice(["AI_CODING", "LINUX", "GITHUB_ACTIONS"], case_sensitive=False),
    help="Filter by category",
)
def history(limit: int, status: str | None, category: str | None):
    """Show content generation history."""
    console.print(BANNER)

    with get_session() as session:
        query = session.query(Topic).order_by(Topic.created_at.desc())

        if status:
            query = query.filter(Topic.status == Status[status.upper()])
        if category:
            query = query.filter(Topic.category == Category[category.upper()])

        records = query.limit(limit).all()

    if not records:
        console.print("[yellow]No records found. Generate some content first![/]")
        console.print("[dim]  python cli.py generate --topic 'Your Topic'[/]")
        return

    status_style = {
        Status.TODO: "white",
        Status.GENERATED: "yellow",
        Status.RECORDED: "cyan",
        Status.PUBLISHED: "bold green",
    }

    table = Table(
        title=f"📊 Content History (last {limit})",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_footer=True,
    )
    table.add_column("ID", style="dim", width=5, justify="right")
    table.add_column("Title", max_width=38)
    table.add_column("Category", justify="center", width=14)
    table.add_column("Status", justify="center", width=11)
    table.add_column("Score", justify="center", width=6)
    table.add_column("Created", justify="right", style="dim", width=12)

    for record in records:
        style = status_style.get(record.status, "white")
        table.add_row(
            str(record.id),
            (record.title or "—")[:38],
            record.category.value if record.category else "—",
            Text(record.status.value, style=style),
            str(record.quality_score) if record.quality_score else "—",
            record.created_at.strftime("%m-%d %H:%M") if record.created_at else "—",
        )

    console.print(table)
    console.print(f"\n[dim]Showing {len(records)} records[/]\n")


# ── SCHEDULE ──────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--days", "-d", default=7, show_default=True, help="Number of days to plan")
def schedule(days: int):
    """Generate a content schedule from pending TODO topics."""
    console.print(BANNER)

    with get_session() as session:
        todo = (
            session.query(Topic)
            .filter(Topic.status == Status.TODO)
            .order_by(Topic.created_at)
            .limit(days * 2)
            .all()
        )

    if not todo:
        console.print("[yellow]⚠  No TODO topics found.[/]")
        console.print("[dim]Add topics: python cli.py generate --topic 'Your Topic'[/]\n")
        return

    from datetime import datetime, timedelta

    table = Table(
        title=f"📅 {days}-Day Content Schedule",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Date", style="bold cyan", width=14)
    table.add_column("📹 Video 1", max_width=35)
    table.add_column("📹 Video 2", max_width=35)

    base = datetime.now().date()
    for i in range(days):
        day = base + timedelta(days=i)
        idx1, idx2 = i * 2, i * 2 + 1
        v1 = todo[idx1].title[:35] if idx1 < len(todo) else "[dim]—[/]"
        v2 = todo[idx2].title[:35] if idx2 < len(todo) else "[dim]—[/]"
        table.add_row(day.strftime("%a, %b %d"), v1, v2)

    console.print(table)
    console.print(f"\n[dim]Target: 2 videos/day → {days * 2} videos in {days} days[/]\n")


# ── STATS ─────────────────────────────────────────────────────────────────────


@cli.command()
def stats():
    """Show content engine statistics."""
    console.print(BANNER)

    with get_session() as session:
        from sqlalchemy import func

        total = session.query(func.count(Topic.id)).scalar() or 0
        by_status = (
            session.query(Topic.status, func.count(Topic.id))
            .group_by(Topic.status)
            .all()
        )
        by_category = (
            session.query(Topic.category, func.count(Topic.id))
            .group_by(Topic.category)
            .all()
        )
        avg_score = session.query(func.avg(Topic.quality_score)).scalar()

    table = Table(title="📈 Engine Statistics", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right", style="cyan")

    table.add_row("Total Topics", str(total))
    table.add_row("Avg Quality Score", f"{avg_score:.1f}/10" if avg_score else "—")

    for status, count in by_status:
        table.add_row(f"  Status: {status.value}", str(count))

    for cat, count in by_category:
        table.add_row(f"  Category: {cat.value}", str(count))

    console.print(table)
    console.print()


# ── TRENDS ────────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--limit", "-n", default=5, show_default=True, help="Number of trending topics to select")
@click.option("--preview", is_flag=True, help="Run the pipeline but do not save to database")
def trends(limit: int, preview: bool):
    """Discover trending developer topics from GitHub, HN, Reddit, and Dev.to."""
    console.print(BANNER)
    
    if preview:
        console.print("[yellow]⚠  Preview mode — results will NOT be saved to database[/]\n")
        
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold blue]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("🔍 Scanning trend sources...", total=1)
        
        try:
            from trends.runner import run_trend_pipeline
            results = run_trend_pipeline(final_limit=limit, save=not preview)
            progress.update(task, description="[bold green]✅ Discovery complete!", completed=1)
        except Exception as exc:
            console.print(f"\n[bold red]❌ Pipeline error: {exc}[/]")
            raise click.Abort() from exc

    if not results:
        console.print("[yellow]No new trending topics found or LLM returned none.[/]")
        return
        
    table = Table(
        title=f"🔥 Top {len(results)} Trending Topics",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True
    )
    table.add_column("Score", justify="right", style="magenta", width=5)
    table.add_column("Source", justify="center", width=10)
    table.add_column("Refined Title / [dim]Raw Title[/]", max_width=50)
    table.add_column("Category", justify="center", width=14)

    for r in results:
        title_display = f"[bold white]{r.title}[/]\n[dim]{r.raw_title[:60]}[/]"
        table.add_row(
            f"{r.trend_score:.1f}" if r.trend_score else "—",
            r.source,
            title_display,
            r.category.value if r.category else "—"
        )

    console.print()
    console.print(table)
    
    if not preview:
        console.print(f"\n[green]💾 Saved {len(results)} topics to database as TODO.[/]")
        console.print("[dim]Run `python cli.py schedule` to view your new queue.[/]\n")


# ── AUTO-PUBLISH ──────────────────────────────────────────────────────────────


@cli.command(name="auto-publish")
def auto_publish():
    """Grab the oldest TODO topic, generate content, and publish to TikTok."""
    console.print(BANNER)

    with get_session() as session:
        topic = (
            session.query(Topic)
            .filter(Topic.status == Status.TODO)
            .order_by(Topic.created_at.asc())
            .first()
        )
        if not topic:
            console.print("[yellow]⚠  No TODO topics found in the database.[/]")
            return
            
        topic_title = topic.title
        topic_id = topic.id

    console.print(f"[bold cyan]🚀 Starting Auto-Publish for Topic:[/] {topic_title}\n")
    
    from engine.graph import run_pipeline

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold blue]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task(f"Generating content & publishing: {topic_title}...", total=1)
        try:
            result = run_pipeline(
                topic=topic_title, 
                audience="developers", 
                generate_audio=True, 
                generate_video=True, 
                publish_tiktok=True
            )
            progress.update(task, description="[bold green]✅ Auto-Publish complete!", completed=1)
        except Exception as exc:
            console.print(f"\n[bold red]❌ Pipeline error: {exc}[/]")
            raise click.Abort() from exc

    # Update database
    with get_session() as session:
        t = session.query(Topic).get(topic_id)
        if t:
            t.status = Status.PUBLISHED
            if "markdown_path" in result:
                t.markdown_path = result["markdown_path"]
            if "quality_score" in result:
                t.quality_score = result["quality_score"]
            
    console.print(f"\n[bold green]🎉 Successfully published and marked as PUBLISHED in database![/]")


@cli.command()
def generate_newsletter():
    """Generates a weekly newsletter from recently published content."""
    console.print("[bold cyan]🚀 Starting Newsletter Generation...[/]")
    from newsletter.agent import generate_weekly_newsletter

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold blue]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("Summarizing published content into a newsletter...", total=1)
        try:
            out_path = generate_weekly_newsletter()
            if out_path:
                progress.update(task, description=f"[bold green]✅ Newsletter generated at {out_path}!", completed=1)
            else:
                progress.update(task, description="[bold yellow]⚠️ No published topics found this week. Nothing to do.", completed=1)
        except Exception as exc:
            console.print(f"\n[bold red]❌ Newsletter error: {exc}[/]")
            raise click.Abort() from exc


@cli.command()
def generate_product():
    """Generates the GitHub Actions Digital Product bundle."""
    console.print("[bold cyan]🚀 Starting Digital Product Generation...[/]")
    from products.github_actions import generate_digital_product

    try:
        out_path = generate_digital_product()
        console.print(f"\n[bold green]🎉 Successfully generated digital product bundle at: {out_path}[/]")
    except Exception as exc:
        console.print(f"\n[bold red]❌ Digital Product generation error: {exc}[/]")
        raise click.Abort() from exc


if __name__ == "__main__":
    cli()
