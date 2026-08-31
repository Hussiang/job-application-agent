import yaml


def load_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def load_profile():
    return load_yaml("config/profile.yaml")


def load_scoring():
    return load_yaml("config/scoring.yaml")
