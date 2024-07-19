import logging
import requests
from pathlib import Path
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn


from trc_cli.provisioner import LeanIXDemoProvisioner
from trc_cli.demo_factory import LeanIXTechDiscoveryDemoFactory
from trc_cli.utils import load_microservices, load_factsheet_ids
from trc_cli.constants import *

logger = logging.getLogger('main')


def run_provision(base_url, api_token):
    session = requests.Session()
    provisioner = LeanIXDemoProvisioner(
        base_url=base_url,
        api_token=api_token,
        session=session
    )

    data_provider = LeanIXTechDiscoveryDemoFactory(
        base_url, api_token, session=session)

    instance_url = provisioner._workspace_info['instance_url']
    workspace_name = provisioner._workspace_info['workspace_name']
    role = provisioner._workspace_info['role']
    workspace_id = provisioner._workspace_info['workspace_id']

    SBOM_VIEW_URL = instance_url + "/" + workspace_name + \
        "/inventory/Application/software-bill-of-materials"

    microservices = load_microservices(MICROSERVICES_PATH)
    print(f"Provisioning Workspace Name: [yellow bold]{workspace_name}[/yellow bold] - ID:[yellow bold]{
          workspace_id}[/yellow bold] - Role:[yellow bold]{role}[/yellow bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=False,
    ) as progress:

        ff_task = progress.add_task(
            description="Setting Feature Flags...", total=1)
        provisioner.enable_feature_flags()
        progress.update(ff_task, completed=1)

        readiness_task = progress.add_task(
            description="Waiting for Workspace to be ready...", total=1)
        provisioner.wait_for_workspace_readiness()
        progress.update(readiness_task, completed=1)

        ms_task = progress.add_task(
            description="Creating microservices...", total=1)
        created_services = data_provider.register_microservice(
            microservices=microservices)
        data_provider.store_microservices(created_services)
        factsheet_ids = load_factsheet_ids()
        progress.update(ms_task, completed=1)

        sbom_task = progress.add_task(
            description="Attaching SBOMs to Microservices...", total=0)
        data_provider.attach_sboms(factsheet_ids=factsheet_ids)
        data_provider.delete_temp_files()
        progress.update(sbom_task, completed=1)

    print(f":computer: Check out the [bold]SBOM View[/bold] at: [bold]{
          SBOM_VIEW_URL} [/bold]")


if __name__ == "__main__":
    run_provision()
