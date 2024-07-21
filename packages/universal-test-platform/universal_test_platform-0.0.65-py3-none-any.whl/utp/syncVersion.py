import subprocess

import click
from utp.getConfig import getCondaConfig
from utp.utils import getSubprocessOutput

def syncVersion():
    versionInConda= _getUtpVersionInConda()
   
    installedVersion = _getInstalledVersion()
    
    if versionInConda != installedVersion :
        subprocess.Popen(["pip", "install", "universal-test-platform=="+versionInConda],).wait()
        click.secho("UTP was synced please try again", bg='black', fg='green')
        exit(1)
        
    


def _getUtpVersionInConda():
    conda = getCondaConfig()
    
    dependencies = conda.get("dependencies")
    
    pip_packages = None

    # Iterate through the dependencies list to find the pip dictionary
    for item in dependencies:
        if isinstance(item, dict) and "pip" in item:
            pip_packages = item["pip"]
            break

    version = None

    for item in pip_packages:
        if isinstance(item, str) and item.startswith("universal-test-platform=="):
            version = item.split("==")[1].strip()
            break
    
    return version



def _getInstalledVersion():
    handler = subprocess.Popen(["pip", "show", "universal-test-platform"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    result = getSubprocessOutput(handler)
    
    installedVersion = None
    
    for item in result.split("\n"):
        if item.strip().startswith("Version:"):
            installedVersion = item.split("Version:")[1].strip()
    
    return installedVersion