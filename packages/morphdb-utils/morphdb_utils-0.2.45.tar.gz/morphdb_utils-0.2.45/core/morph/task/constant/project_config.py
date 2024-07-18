import os


class ProjectConfig:
    # Directories
    INIT_DIR = os.path.expanduser("~/.morph")
    RUNS_DIR = os.path.expanduser("~/.morph/runs")
    OUTPUTS_DIR = "data/outputs"
    # Files
    MORPH_CRED_PATH = os.path.expanduser("~/.morph/credentials")
    MORPH_YAML = "morph.yaml"
    MORPH_PROFILE_PATH = os.path.expanduser("~/.morph/profiles.yaml")
