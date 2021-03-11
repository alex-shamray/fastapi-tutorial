import typer
from pydantic import ValidationError

from app import crud
from app.db.session import SessionLocal
from app.password_validation import validate_password

app = typer.Typer(help="CLI user manager.")


@app.command()
def createsuperuser(
    email: str = typer.Argument(
        ..., help="Specifies the login for the superuser."
    )
):
    """
    Used to create a superuser.
    """
    typer.echo(email)


def _get_pass(prompt=''):
    p = typer.prompt(prompt)
    if not p:
        raise typer.Abort()
    return p


@app.command()
def changepassword(
    email: str = typer.Argument(
        ..., help="Email to change password for."
    ),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
):
    """
    Change a user's password for app.models.user.User.
    """
    db = SessionLocal()
    user = crud.user.get_by_email(db, email=email)
    if not user:
        typer.secho("user '%s' does not exist" % email, fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.echo("Changing password for user '%s'" % user)

    try:
        validate_password(password, user)
    except ValidationError as err:
        typer.secho('\n'.join(err.messages), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    crud.user.update(db, db_obj=user, obj_in={'password': password})

    typer.echo("Password changed successfully for user '%s'" % user)


if __name__ == "__main__":
    app()
