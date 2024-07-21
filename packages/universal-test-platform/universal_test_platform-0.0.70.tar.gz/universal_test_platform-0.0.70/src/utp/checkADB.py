import click

from utp.utils import readCommand


def checkADB():
    #check java installed
    adbStatus,adbError = readCommand("adb")
    
    if adbError or adbStatus.count("Android Debug Bridge version") <= 0:
        click.secho("ADB is not installed please install adb or android studio, then continue with utp", bg='black', fg='yellow')
 
        exit(1)
        
        
