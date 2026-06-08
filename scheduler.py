import time
import schedule
import subprocess
from rich.console import Console

console = Console()

def run_trends():
    console.print("\n[bold blue]🚀 Running scheduled task: cli.py trends[/]")
    subprocess.run(["python", "cli.py", "trends"])

def run_auto_publish():
    console.print("\n[bold magenta]🎥 Running scheduled task: cli.py auto-publish[/]")
    subprocess.run(["python", "cli.py", "auto-publish"])

def run_newsletter():
    console.print("\n[bold green]📧 Running scheduled task: cli.py generate-newsletter[/]")
    subprocess.run(["python", "cli.py", "generate-newsletter"])

# Schedule trends to run every morning at 08:00
schedule.every().day.at("08:00").do(run_trends)

# Schedule auto-publish to run twice a day (12:00 PM and 17:00 PM)
schedule.every().day.at("12:00").do(run_auto_publish)
schedule.every().day.at("17:00").do(run_auto_publish)

# Schedule newsletter generation every Friday at 09:00
schedule.every().friday.at("09:00").do(run_newsletter)

if __name__ == "__main__":
    console.print("[bold green]🤖 Automate.sh Scheduler Started![/]")
    console.print("Scheduled Jobs:")
    for job in schedule.jobs:
        console.print(f" - {job}")
    
    # Run the trends once on startup just to be sure
    # run_trends()
    
    while True:
        schedule.run_pending()
        time.sleep(60)
