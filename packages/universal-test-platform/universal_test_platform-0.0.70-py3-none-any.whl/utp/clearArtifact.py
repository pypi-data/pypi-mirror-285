import os
import shutil
from utp.getConfig import getConfig

def clearArtifact():
      
      config = getConfig()
      
      return removeTree(os.getcwd()+"/"+config.get("artifactsDir"))
    

def removeTree(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
        return True
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
        return True
    else:
        return False