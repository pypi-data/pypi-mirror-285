import sys
import click
from .auth import auth_group
from clisync import CliSync


def main():
    import pyhectiqlab
    from pyhectiqlab import const
    from pyhectiqlab import Run, Model, Dataset
    from pyhectiqlab.project import Project
    from pyhectiqlab.artifact import Artifact
    from pyhectiqlab.tag import Tag
    from pyhectiqlab.message import Message
    from pyhectiqlab.versions import PackageVersion

    # enable block and project creation for the cli
    const.DISABLE_PROJECT_CREATION = False

    group = CliSync(module=pyhectiqlab, classes=[Run, Model, Dataset, Artifact, Tag, Project, PackageVersion, Message])
    cli = click.CommandCollection(
        sources=[auth_group, group], help="👋 Hectiq Lab CLI. Documentation at https://docs.hectiq.ai."
    )
    # Standalone mode is False so that the errors can be caught by the runs
    cli(standalone_mode=False)
    sys.exit()


if __name__ == "__main__":
    main()
