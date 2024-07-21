import copy
import sys

import requests
import yaml


def merge(data):
    includes = data.get("include")
    if not includes:
        return data

    for include in includes:
        if include.startswith("http://") or include.startswith("https://"):
            result = requests.get(include, timeout=10)
            result.raise_for_status()
            include_data = yaml.safe_load(result.text)

            # Source is what we have in our file
            # Destination is what we just loaded and will replace previous
            # questions
            src_questions = copy.deepcopy(data["questions"])
            dst_questions = include_data["questions"]

            src_questions = {x["name"]: x for x in src_questions}
            dst_questions = {x["name"]: x for x in dst_questions}

            dst_questions = {**dst_questions, **src_questions}
            data["questions"] = [v for k, v in dst_questions.items()]

        else:
            sys.exit("error: inclusion method not implemented")
    return data
