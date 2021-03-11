import typer

from app import crud
from app.db.session import SessionLocal

app = typer.Typer(help="CLI user manager.")


@app.command()
def createsuperuser(
    email: str = typer.Argument(
        ..., help="Specifies the login for the superuser."
    ),
):
    """
    Used to create a superuser.
    """
    typer.echo(email)


@app.command()
def changepassword(
    email: str = typer.Argument(
        ..., help="Email to change password for."
    )
):
    """
    Change a user's password for app.models.user.User.
    """
    db = SessionLocal()
    user = crud.user.get_by_email(db, email=email)
    typer.echo(user)


if __name__ == "__main__":
    app()
