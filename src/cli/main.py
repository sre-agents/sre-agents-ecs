import typer

app = typer.Typer(name="arkrun")


@app.command()
def deploy():
    pass


@app.command()
def login(ak: str, sk: str):
    pass


@app.command()
def version():
    print("Internal test version.")


if __name__ == "__main__":
    app()
