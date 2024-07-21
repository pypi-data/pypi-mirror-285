from enum import Enum
import os
import platform
import click
from utp.utils import readCommand

class OS(Enum):
    LINUX = "Linux"
    WINDOWS = "Windows"
    DARWIN = "Darwin"

def checkRobocorp():
    #check robocorp installed
    javaStatus = os.popen("rcc --version").read()
    if javaStatus.startswith("v") != True:
        if platform.system() == OS.LINUX.value:
            stdout, stderr = readCommand("""curl -o rcc https://downloads.robocorp.com/rcc/releases/latest/linux64/rcc ;
                    chmod a+x rcc ;
                    mv rcc /usr/local/bin/ ;
                    """)
            if stderr:
               click.secho("Can't install rcc", bg='black', fg='red')
               exit(1)
            
        elif platform.system() == OS.DARWIN.value:
            os.popen("""brew update ;
                    brew install robocorp/tools/rcc ;
                    """).read()
        elif platform.system() == OS.WINDOWS.value:
              click.secho("""
                    Open the command prompt
                    Download: curl -o rcc.exe https://downloads.robocorp.com/rcc/releases/latest/windows64/rcc.exe
                    Add to system path (https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10): Open Start -> Edit the system environment variables
                    Test: rcc
                    """,bg='black', fg='white')
              click.secho("Try again after rcc installed", bg='black', fg='yellow')
              
              exit(1)
        else:
            logGuid()
            
        click.secho("rcc installed successfully", bg='black', fg='green')



def logGuid():
    click.secho("""
        Windows
            - Open the command prompt
            - Download: curl -o rcc.exe https://downloads.robocorp.com/rcc/releases/latest/windows64/rcc.exe
            - Add to system path: Open Start -> Edit the system environment variables
            - Test: rcc

        macOS
            - Brew cask from Robocorp tap
            - Update brew: brew update
            - Install: brew install robocorp/tools/rcc
            - Test: rcc
            - Upgrading: brew upgrade rcc

        Linux
            - Open the terminal
            - Download: curl -o rcc https://downloads.robocorp.com/rcc/releases/latest/linux64/rcc
            - Make the downloaded file executable: chmod a+x rcc
            - Add to path: sudo mv rcc /usr/local/bin/
            - Test: rcc
        """, bg='black', fg='yellow')