"""gish — top-level click group."""

import click

from gshell_memory.cli.archive import archive_group
from gshell_memory.cli.audit import audit_cmd
from gshell_memory.cli.carryover import carryover_group
from gshell_memory.cli.doctor import doctor_cmd
from gshell_memory.cli.enum import enum_group
from gshell_memory.cli.init import init_cmd
from gshell_memory.cli.log import log_cmd
from gshell_memory.cli.migrate import migrate_cmd
from gshell_memory.cli.recall import recall_cmd
from gshell_memory.cli.run import run_maintenance_cmd
from gshell_memory.cli.sop import sop_group
from gshell_memory.cli.version import version_cmd


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
gish.add_command(migrate_cmd)
gish.add_command(sop_group)
gish.add_command(archive_group)
gish.add_command(carryover_group)
gish.add_command(enum_group)
