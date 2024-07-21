import subprocess
from typing import IO, Optional
import click
import requests
from tqdm import tqdm

def getSubprocessOutput(process: subprocess.Popen[bytes]):

    def log_subprocess_output(pipe: Optional[IO[bytes]]):
        result= ""
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            a=result + line.decode("utf-8")
            result = a
            
        return result
    
    with process.stdout:
       appiumStatus= log_subprocess_output(process.stdout)
    process.wait() # 0 means success

    return appiumStatus





def readCommand(command):
# Run the command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Get the output and errors
    stdout, stderr = process.communicate()


    return (stdout.decode(),stderr.decode())


def downloadFile(url: str, name: str):
    # Streaming, so we can iterate over the response.
    response = requests.get(url, stream=True)

    # Sizes in bytes.
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    try:
        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with open(name, "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

        if total_size != 0 and progress_bar.n != total_size:
            raise RuntimeError("Could not download file")
    except:
        click.launch('https://github.com/SeleniumHQ/selenium/releases/tag/selenium-4.21.0')
        click.secho("""
                    https://github.com/SeleniumHQ/selenium/releases/tag/selenium-4.21.0
                    Download selenium hub and move it to .cache folder""")
        
        raise RuntimeError("Could not download file")
    