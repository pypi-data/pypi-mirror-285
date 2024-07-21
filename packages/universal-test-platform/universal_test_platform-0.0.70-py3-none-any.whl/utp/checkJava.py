import subprocess
import click

from utp.utils import getSubprocessOutput

FINAL_FILE_PATH = "https://www.oracle.com/java/technologies/downloads/?er=221886"

def checkJava():
    #check java installed
    process = subprocess.Popen(["java", "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    javaStatus= getSubprocessOutput(process)

    if javaStatus.count("openjdk") <=0 and javaStatus.count("Java HotSpot") <=0:
        click.secho("Download Java jdk and install it", bg='black', fg='yellow')
 
        click.launch(FINAL_FILE_PATH)

        click.secho("Run again after installation is finished", bg='black', fg='yellow')
        exit(1)
        
        
