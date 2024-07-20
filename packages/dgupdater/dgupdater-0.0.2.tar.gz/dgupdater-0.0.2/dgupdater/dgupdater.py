from click import group, command

@group()
def cli():
    pass

@command()
def init():
    # click.echo("Initializing dgupdater...")
    print("Initializing dgupdater...")



cli.add_command(init)

if __name__ == "__main__":
    cli()
