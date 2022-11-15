import sys
import subprocess
import pkg_resources


def check_module():
    required  = {'pandas', 'requests', 'urllib3', 'xmltodict'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing   = required - installed

    if missing:
        # implement pip as a subprocess:
        subprocess.check_call([sys.executable, '-m', 'pip3', 'install', *missing])
