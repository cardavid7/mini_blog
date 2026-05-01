import typer
import app.seeds.service as service

app = typer.Typer(help="run seed scripts, seeding categories, tags and users")

@app.command(name="all")
def all_():
    """Seed all"""
    service.run_all()
    typer.echo("All seeded")

@app.command("users")
def users():
    """Seed users"""
    service.run_users()
    typer.echo("Users seeded")
    
@app.command("categories")
def categories():
    """Seed categories"""
    service.run_categories()
    typer.echo("Categories seeded")
    
@app.command("tags")
def tags():
    """Seed tags"""
    service.run_tags()
    typer.echo("Tags seeded")

@app.command(name="all")
def seed_all():
    """Seed all"""
    service.run_users()
    service.run_categories()
    service.run_tags()