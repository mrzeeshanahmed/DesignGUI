import typer

app = typer.Typer(help="Nice Design OS CLI")

@app.command()
def init():
    """Initialize a new Nice Design OS project."""
    typer.echo("Init command - to be implemented in Phase 3.")

@app.command()
def start():
    """Start the Live Preview Engine."""
    typer.echo("Start command - to be implemented in Phase 4.")

if __name__ == "__main__":
    app()
