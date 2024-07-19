import typer
import os
from typing_extensions import Annotated
from trc_cli.run import run_provision
from dotenv import load_dotenv
import logging

dotenv_path = os.path.join(os.getcwd(), '.env')


app = typer.Typer(rich_markup_mode='rich')

logger = logging.getLogger("main")
handler = logging.StreamHandler()
handler.setLevel(logging.WARN)
logger.addHandler(handler)


@app.command()
def main(provision: Annotated[bool, typer.Option("--provision", "-p",
                                                 help="Provisions the workspace and adds sample data.")] = False,
         debug: Annotated[bool, typer.Option("--debug",
                                             help="Set the logs to DEBUG")] = False):
    """
    Technology Risk and Governance CLI to provision demo workspaces.
    """

    if debug:
        handler.setLevel(10)
        logger.setLevel(10)

        logger.info("DEBUG MODE")

    if provision:

        if load_dotenv(dotenv_path):
            API_TOKEN = os.getenv("APITOKEN")
            BASE_URL = os.getenv("HOST")

        else:
            BASE_URL = typer.prompt("Enter your host name e.g. demo-eu-2 ", hide_input=False,
                                    )
            API_TOKEN = typer.prompt(
                "Enter your API Token", hide_input=True)

    run_provision(base_url=BASE_URL, api_token=API_TOKEN)


if __name__ == "__main__":

    app()
