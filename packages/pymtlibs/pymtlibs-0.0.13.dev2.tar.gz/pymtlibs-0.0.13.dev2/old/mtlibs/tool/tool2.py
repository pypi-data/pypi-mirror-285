import argparse
import logging
import os
import sys
from urllib.parse import urlparse
import subprocess
from subprocess import run 

from mtlibs import mtutils

logger = logging.getLogger(__name__)


def main():
    cmd = "ls"
    cmd2 = f"jjdk skdj"
    process = run(cmd2, shell=True)

    print(run("env"))

if __name__ == "__main__":
    main()