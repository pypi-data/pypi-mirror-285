def parse_version_label(label: str):
    name = None
    version = "latest"

    if label is None:
        return name, version

    separator_count = label.count(":")

    if separator_count == 0:
        name = label
    elif separator_count == 1:
        name, version = label.split(":")
    else:
        raise Exception("Invalid label format")

    return name, version


def validate_name(name: str):
    pass


def validate_version(version: str):
    pass


def generate_label(name: str, version: str = "latest"):
    label = ":".join([name, version])

    return label
