import click

from anyscale.commands.llm.dataset_commands import dataset_cli


@click.group(
    "llm", help="Interact with Anyscale's LLM APIs.", hidden=True,
)
def llm_cli():
    pass


llm_cli.add_command(dataset_cli)
