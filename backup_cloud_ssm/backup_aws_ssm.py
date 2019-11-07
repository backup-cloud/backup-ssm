from backup_cloud_ssm.aws_ssm_dict import aws_ssm_dict
import json
import logging
import sys

logger = logging.getLogger()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def backup_to_file(file):
    ssm_dict = aws_ssm_dict()
    contents = {}
    for i in ssm_dict.keys():
        try:
            contents[i] = ssm_dict[i]
        except KeyError:
            eprint("failed to find expected parameter:", i)
            raise
    try:
        with open(file, "w") as f:
            json.dump(contents, f)
    except TypeError:
        json.dump(contents, file)


def restore_from_file(file):
    ssm_dict = aws_ssm_dict()
    try:
        with open(file) as f:
            contents = json.load(f)
    except TypeError:
        contents = json.load(file)
    for i in contents.keys():
        try:
            ssm_dict[i] = contents[i]
        except ssm_dict.exceptions.ParameterAlreadyExists:
            logger.warning("Parameter " + i + " already exists!")
