import click
import time
import subprocess
from utp.checkSuccess import checkSuccess
from utp.webVariables import webVariables
from utp.syncVersion import syncVersion
from utp.appVariables import appVariables
from utp.checkADB import checkADB
from utp.checkAppium import checkAppium
from utp.checkJava import checkJava
from utp.checkNode import checkNode
from utp.checkRobocorp import checkRobocorp
from utp.checkRobotFramework import checkRobotFramework
from utp.clearArtifact import clearArtifact
from utp.localHub import runLocalHub
from utp.checkport import isPortUsed


@click.group()
def cli():
    pass

@click.command()
@click.option('--remote', '-r',  'remote', is_flag=True)
@click.option('--path', '-p',  'path')
@click.option('--noReset', '-p',  'noReset', is_flag=True)
def web(remote, path, noReset):
    """Run test cases locally"""

    syncVersion()

    #check node installed
    checkNode()

    checkJava()
    
    hubHandler= None

    if not remote:
        hubHandler = runLocalHub()

    checkRobotFramework()

    checkRobocorp()

    clearArtifact()
    
    env = webVariables(remote, path, noReset)

    subprocess.Popen(["rcc", "run", "--task", "Web"],env=env).wait()
    
    if hubHandler is not None:
        hubHandler.kill()
    
    if not checkSuccess():
        exit(1)
        

@click.command()
@click.option('--android_app', '-aa', 'androidApp')
@click.option('--android_platform_version', '-apv', 'androidPlatformVersion')
@click.option('--remote', '-r',  'remote', is_flag=True)
@click.option('--path', '-p',  'path')
@click.option('--noReset', '-p',  'noReset', is_flag=True)
def app(androidApp, androidPlatformVersion, remote, path, noReset):
    """Run test cases locally"""

    syncVersion()

    #check node installed
    checkNode()
    
    if not remote:
       checkADB()

    appiumHandler = None
    if not remote:
        appiumHandler= checkAppium()
        
    checkRobotFramework()

    checkRobocorp()

    clearArtifact()
    

    env = appVariables(androidApp, androidPlatformVersion, remote, path, noReset)
    
    subprocess.Popen(["rcc", "run", "--task", "App"],env=env).wait()
    if appiumHandler is not None:
        appiumHandler.kill()
    
    if not checkSuccess():
        exit(1)

    
# @click.command()
# @click.Choice()
cli.add_command(web)
cli.add_command(app)

if __name__ == '__main__':
    cli()