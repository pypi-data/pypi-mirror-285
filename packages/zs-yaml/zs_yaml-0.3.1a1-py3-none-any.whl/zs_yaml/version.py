import subprocess
import os


def read_version():
    # Try to read version from the VERSION file in the package directory
    try:
        with open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        # If not found, try to read from the project root (for development mode)
        try:
            with open(os.path.join(os.path.dirname(__file__), '..', 'VERSION'), 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "unknown"


VERSION = read_version()
COMMIT_ID = "n/a(dev-mode)"


def get_git_revision_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except:
        return None


def get_version_info():
    return f"{VERSION} (commit: {COMMIT_ID})"


# During package installation, this will be replaced with the actual commit ID
if os.path.exists(os.path.join(os.path.dirname(__file__), '.git_commit')):
    with open(os.path.join(os.path.dirname(__file__), '.git_commit'), 'r') as f:
        COMMIT_ID = f.read().strip()
