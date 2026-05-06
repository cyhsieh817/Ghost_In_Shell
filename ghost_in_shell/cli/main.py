"""gish — top-level click group."""

import click

from ghost_in_shell.cli.audit import audit_cmd
from ghost_in_shell.cli.doctor import doctor_cmd
from ghost_in_shell.cli.init import init_cmd
from ghost_in_shell.cli.log import log_cmd
from ghost_in_shell.cli.recall import recall_cmd
from ghost_in_shell.cli.run import run_maintenance_cmd
from ghost_in_shell.cli.version import version_cmd


@click.group(
    name="gish",
    help="Ghost In Shell — multi-CLI agent memory framework.",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def gish() -> None:
    pass


gish.add_command(version_cmd)
gish.add_command(init_cmd)
gish.add_command(doctor_cmd)
gish.add_command(recall_cmd)
gish.add_command(audit_cmd)
gish.add_command(run_maintenance_cmd)
gish.add_command(log_cmd)
