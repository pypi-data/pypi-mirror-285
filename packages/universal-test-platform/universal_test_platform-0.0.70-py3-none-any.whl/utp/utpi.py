import os
import click
import subprocess
from utp.checkSuccess import checkSuccess
from utp.webVariables import webVariables
from utp.appVariables import appVariables
from utp.checkRobocorp import checkRobocorp
from utp.checkRobotFramework import checkRobotFramework


@click.group("internal cli")
def internal_cli():
    pass

@click.command("web-pipeline")
def webPipeline():
    """Run test cases pipeline"""

    checkRobotFramework()

    checkRobocorp()
    
    env = webVariables(remote=True)

    subprocess.Popen(["rcc", "run", "--task", "Web"],env=env).wait()
    
    if not checkSuccess():
        exit(1)


@click.command("app-pipeline")
@click.option('--android_app', '-aa', 'androidApp')
@click.option('--android_platform_version', '-apv', 'androidPlatformVersion')
def appPipeline(androidApp, androidPlatformVersion):
    """Run test cases pipeline"""

    checkRobotFramework()

    checkRobocorp()

    env = appVariables(androidApp, androidPlatformVersion, remote=True)
    
    subprocess.Popen(["rcc", "run", "--task", "App"],env=env).wait()
    
    if not checkSuccess():
        exit(1)
    

@click.command("app-rcc",help="run robot test for app by rcc, this shouldn't call directly")
def appRcc():
    env = os.environ
    
    testPath = env["TEST_PATH"] or "src/App/"
    subprocess.Popen('python -m robot --report NONE --outputdir output --logtitle "Task log" ' + testPath ,shell=True,env=os.environ).wait()
    

@click.command("web-rcc",help="run robot test for app by rcc, this shouldn't call directly")
def webRcc():
    env = os.environ
    
    testPath = env["TEST_PATH"] or "src/Web/"
    subprocess.Popen('python -m robot --report NONE --outputdir output --logtitle "Task log" ' + testPath,shell=True,env=os.environ).wait()
    
internal_cli.add_command(appPipeline)
internal_cli.add_command(webPipeline)
internal_cli.add_command(appRcc)
internal_cli.add_command(webRcc)

if __name__ == '__main__':
    internal_cli()