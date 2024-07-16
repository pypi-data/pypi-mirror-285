import click
from indian_repair.os_restart import restart

@click.command()
def cli():
    """Restart the computer based on the detected operating system."""
    restart()

if __name__ == '__main__':
    cli()
