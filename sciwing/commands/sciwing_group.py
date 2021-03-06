import click
from sciwing.commands.new import new
from sciwing.commands.run import run
from sciwing.commands.test import test
from sciwing.commands.develop import develop
from sciwing.commands.download import download


@click.group(name="sciwing")
def sciwing_group():
    """Root command for everything else in sciwing
    """
    pass


def main():
    sciwing_group.add_command(new)
    sciwing_group.add_command(run)
    sciwing_group.add_command(test)
    sciwing_group.add_command(develop)
    sciwing_group.add_command(download)
    sciwing_group()


if __name__ == "__main__":
    main()
