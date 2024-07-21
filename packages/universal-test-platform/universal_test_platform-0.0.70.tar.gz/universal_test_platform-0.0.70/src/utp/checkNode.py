import os
import click

def checkNode():
    """check node installed"""
    nodeStatus = os.popen("node -v").read()
    if nodeStatus.startswith("v") != True:
        click.secho("Nodejs is not installed please install it", bg='black', fg='red')
        click.launch("https://nodejs.org/en/download/package-manager")
        click.secho("Run again, After installation is finished", bg='black', fg='yellow')
        exit(1)
