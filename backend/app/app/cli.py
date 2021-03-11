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


def _get_pass(prompt="Password"):
    p = typer.prompt(prompt)
    if not p:
        raise typer.Abort()
    return p


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
    if not user:
        typer.echo("user '%s' does not exist" % email, err=True)
        raise typer.Exit(code=1)

    typer.echo("Changing password for user '%s'" % user)

    MAX_TRIES = 3
    count = 0
    p1, p2 = 1, 2  # To make them initially mismatch.
    password_validated = False
    while (p1 != p2 or not password_validated) and count < MAX_TRIES:
        p1 = _get_pass()
        p2 = _get_pass("Password (again)")
        if p1 != p2:
            typer.echo('Passwords do not match. Please try again.')
            count += 1
            # Don't validate passwords that don't match.
            continue
        try:
            validate_password(p2, user)
        except ValidationError as err:
            typer.echo('\n'.join(err.messages), err=True)
            count += 1
        else:
            password_validated = True

    if count == MAX_TRIES:
        typer.echo("Aborting password change for user '%s' after %s attempts" % (user, count), err=True)
        raise typer.Exit(code=1)

    crud.user.update(db, db_obj=user, obj_in={'password': p1})

    typer.echo("Password changed successfully for user '%s'" % user)


if __name__ == "__main__":
    app()
