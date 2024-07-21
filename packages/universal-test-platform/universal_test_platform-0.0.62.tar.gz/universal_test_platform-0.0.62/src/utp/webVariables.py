import os
from typing import Optional

def webVariables(remote: Optional[bool] = False, path: Optional[bool] = None, noReset: Optional[bool] = None,):
    my_env = os.environ
    my_env['REMOTE'] = str(remote) if remote else ""
    my_env['TEST_PATH'] = path if path else ""
    my_env['NO_RESET'] = noReset if noReset else ""

    return my_env
    