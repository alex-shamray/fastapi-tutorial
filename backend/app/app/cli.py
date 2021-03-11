import typer

app = typer.Typer()


@app.command()
def createsuperuser():
    """
    Used to create a superuser.
    """
    pass


@app.command()
def changepassword(email: str = ""):
    """
    Change a user's password for app.models.user.User.
    """
    pass


if __name__ == "__main__":
    app()
