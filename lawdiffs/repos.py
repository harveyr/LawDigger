import os
import subprocess
import shlex
import logging
import shutil

logger = logging.getLogger(__name__)

REPO_TOP_DIR = os.path.join(
    os.path.split(__file__)[0],
    'repos')


def get_repo_path(repo_rel_path):
    return os.path.join(REPO_TOP_DIR, repo_rel_path)


def run_git_command(command, repo_rel_path):
    command = ['git'] + shlex.split(command)
    working_dir = get_repo_path(repo_rel_path)

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
        return out.decode('utf-8').encode('utf-8')


def wipe_and_init(repo_rel_path):
    repo_path = get_repo_path(repo_rel_path)
    try:
        shutil.rmtree(repo_path)
    except OSError:
        pass
    os.makedirs(repo_path)
    run_git_command('init', repo_rel_path)


def ensure_repo(repo_rel_path):
    repo_path = get_repo_path(repo_rel_path)
    if not (os.path.exists(repo_path) and os.path.isdir(repo_path)):
        wipe_and_init(repo_rel_path)


def update(laws, tag_name, repo_rel_path):
    logger.debug('tag_name: {v}'.format(v=tag_name))
    ensure_repo(repo_rel_path)

    repo_path = get_repo_path(repo_rel_path)
    for law in laws:
        f_path = os.path.join(repo_path, law.filename)
        with open(f_path, 'w') as open_f:
            open_f.write(law.full_law)

    run_git_command('init', repo_rel_path)
    run_git_command('add -A', repo_rel_path)
    run_git_command('commit -m "Testing"', repo_rel_path)
    run_git_command(
        'tag -a {tag} -m "{tag}"'.format(tag=tag_name), repo_rel_path)


def get_tag_diff(filename, tag1, tag2, repo_rel_path):
    cmd = 'diff {tag1} {tag2} {file}'.format(
        tag1=tag1, tag2=tag2, file=filename)
    return run_git_command(cmd, repo_rel_path)
