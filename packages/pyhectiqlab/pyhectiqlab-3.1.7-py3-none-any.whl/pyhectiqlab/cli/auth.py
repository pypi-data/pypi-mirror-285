import click


@click.group()
def auth_group():
    pass


@auth_group.command("authenticate", help="Authenticate to the Hectiq Lab.")
@click.option(
    "--generate",
    "only_generate",
    is_flag=True,
    default=False,
    help="If True, the key is only generated and not saved on your computer. Use this option if you want to use the key on another device.",
)
def authenticate(only_generate: bool):
    """Authenticate to the Hectiq Console."""
    import httpx
    import os
    import toml
    from pathlib import Path
    from pyhectiqlab.auth import is_authenticated
    from pyhectiqlab import API_URL
    from pyhectiqlab.settings import getenv

    if only_generate:
        click.secho(
            "🚨 Mode is set to generate only. The key will not be saved on your computer. At the end of the authentification, the key will be shown.",
            fg="cyan",
        )
    else:
        click.secho("👋 Welcome!")

    is_logged = is_authenticated()

    if is_logged and not only_generate:
        # Ask if the user wants to add a new key
        click.secho("You are already logged in.", fg="green")
        should_continue = click.prompt(
            "Do you still want to continue and create a new API key?",
            default="y",
            show_default=True,
            type=click.Choice(["y", "n"]),
        )
        if should_continue == "n":
            return

    # Accessing the user using basic authentication
    click.secho("Please enter your credentials.")
    email = click.prompt("Email", type=str)
    password = click.prompt("Password", type=str, hide_input=True)

    try:
        import socket

        name = socket.gethostname()
    except:
        name = "[unknown hostname]"
    credentials_path = getenv("HECTIQLAB_CREDENTIALS", os.path.join(Path.home(), ".hectiq-lab", "credentials.toml"))
    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)

    # Get the API key
    auth = httpx.BasicAuth(username=email, password=password)
    body = dict(name=name)
    res = httpx.post(f"{API_URL}/app/auth/api-keys", json=body, auth=auth)
    if res.status_code != 200:
        click.echo("Authentication failed.")
        click.echo(res)
        return
    api_key = res.json()

    # Save the key in .hectiq-lab/credentials
    if not only_generate:
        with open(credentials_path, "a") as f:
            # Dump as TOML
            data = {}
            data[name] = api_key
            toml.dump(data, f)
            f.write("\n")
            click.echo(f"A new API key has been added to {credentials_path}.")
    else:
        click.secho("--------------------------------------------------------------------\n🔑 Your API key:")
        click.secho(f"{api_key['value']}", bold=True)
        click.secho("--------------------------------------------------------------------\n")
        click.secho(
            "⚠️ The value above is your API key. It won't be show again and the key has not been saved on your computer.",
            bg="red",
            fg="white",
            bold=True,
        )
        click.echo(
            "Use the env `HECTIQLAB_API_KEY` to authenticate with this key or visit https://docs.hectiq.ai/authenticate.html to learn how to use the key."
        )
        return

    click.secho("You are now logged in.", fg="green")
