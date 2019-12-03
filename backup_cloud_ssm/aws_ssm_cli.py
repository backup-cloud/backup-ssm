import argparse
import sys
import backup_cloud_ssm


def main():
    parser = argparse.ArgumentParser(description="Backup AWS SSM Parameter Store")
    parser.add_argument("--restore", help="restore from stdin", action="store_true")
    args = parser.parse_args()
    if args.restore:
        backup_cloud_ssm.restore_from_file(sys.stdin)
    else:
        backup_cloud_ssm.backup_to_file(sys.stdout)


if __name__ == "__main__":
    main()
