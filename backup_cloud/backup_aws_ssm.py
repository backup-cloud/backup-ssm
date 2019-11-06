from backup_cloud.aws_ssm_dict import aws_ssm_dict
import json


def backup_to_file(filename):
    ssm_dict = aws_ssm_dict()
    contents = {}
    for i in ssm_dict.keys():
        contents[i] = ssm_dict[i]
    with open(filename, "w") as f:
        json.dump(contents, f)


def restore_from_file(filename):
    ssm_dict = aws_ssm_dict()
    with open(filename) as f:
        contents = json.load(f)
    for i in contents.keys():
        ssm_dict[i] = contents[i]
