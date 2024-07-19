#!/usr/bin/env python

import argparse
import os
import datetime
import time


def parse_arguments():
    parser = argparse.ArgumentParser(description='Watches a folder for changes and triggers an event')
    parser.add_argument('watched_folder', type=str, help='name of the package as it will called from pip')
    parser.add_argument('-a', '--action', action="append", type=str, help='action to take when change is detected (usage: pattern:command)', required=False)
    parser.add_argument('-r', '--recursive', action='store_true', help='include subdirectories')
    args = parser.parse_args()
    return args


def get_updated_files(folder: str, since: datetime.datetime):
    updated_files = []
    last_update = since
    for root, dirs, files in os.walk(folder):
        for filename in files:
            # print(filename)
            file_path = os.path.join(root, filename)
            file_stat = os.stat(file_path)
            modification_time = file_stat.st_mtime
            creation_time = file_stat.st_ctime
            modification_datetime = datetime.datetime.fromtimestamp(modification_time)
            creation_datetime = datetime.datetime.fromtimestamp(creation_time)
            update_datetime = max(modification_datetime, creation_datetime)
            if update_datetime > since:
                updated_files.append(file_path)
                if update_datetime > last_update:
                    last_update = update_datetime
    return updated_files, last_update


def get_command(file_path: str, actions: {}):
    for pattern, command in actions.items():
        if file_path.endswith(pattern):
            return command
    return None


def main():
    try:
        args = parse_arguments()

        if not os.path.exists(args.watched_folder):
            print(f'The folder {args.watched_folder} does not exist')
            exit(1)

        actions = {}
        if args.action:
            for action in args.action:
                pattern, command = action.split(':')
                actions[pattern] = command

        last_update = datetime.datetime.now()
        while True:
            time.sleep(1)
            updated_files, last_update = get_updated_files(args.watched_folder, last_update)
            for updated_file in updated_files:
                command = get_command(updated_file, actions)
                if command:
                    os.system(command.format(updated_file=updated_file))

    except argparse.ArgumentError as e:
        print("Error:", e)
        exit(1)


if __name__ == "__main__":
    main()
