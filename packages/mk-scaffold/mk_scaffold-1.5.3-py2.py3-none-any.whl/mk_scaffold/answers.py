import sys

import yaml


def load(args, data):
    """
    Load an answers file
    """
    file = args.get("input_file")
    if not file:
        return data

    try:
        with open(file, encoding="UTF-8") as fd:
            answers = yaml.safe_load(fd)
    except Exception as err:
        sys.exit(f"error: failed to open '{file}': {err}")

    # Copy answers without emptying out values that could have been present
    # in questions file.
    if "answers" not in data:
        data["answers"] = {}
    if not answers:
        return data
    for k, v in answers.get("answers").items():
        data["answers"][k] = v
    return data
