import subprocess
import sys
import click

def checkRobotFramework():
   #check robotframework installed
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
    if installed_packages.count("robotframework") <= 0:
        subprocess.check_output([sys.executable, '-m', 'pip', 'install', 'robotframework'])
        click.secho("robotframework installed successfully", bg='black', fg='green')
