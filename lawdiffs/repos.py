import os
import subprocess
import shlex
import logging

logger = logging.getLogger(__name__)

REPO_TOP_DIR = os.path.join(
    os.path.split(__file__)[0],
    'repos')


def run_git_command(command, repo_rel_path):
    command = ['git'] + shlex.split(command)
    working_dir = os.path.join(REPO_TOP_DIR, repo_rel_path)

    p = subprocess.Popen(
        command,
        cwd=working_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    out, err = p.communicate()
    if err:
        logger.error(err.decode('utf-8'))
        return None
    else:
        return out.decode('utf-8')

