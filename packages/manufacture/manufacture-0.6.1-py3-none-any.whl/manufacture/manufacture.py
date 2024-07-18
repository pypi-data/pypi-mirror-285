import os
import sys
import shutil
import time
from pathlib import Path


def create_file(filenames):
    for filename in filenames:
        with open(filename, 'w') as f:
            pass
        print(f"Created file {filename}")


def add_content(filename, content):
    if os.path.exists(filename):
        with open(filename, 'a') as f:
            f.write(content)
        print(f"Added content to {filename}")
    else:
        print(f"Error: {filename} does not exist")


def change_file(oldname, newname, backup=False):
    if os.path.exists(oldname):
        if backup:
            backup_name = f"{oldname}.bak"
            shutil.copy2(oldname, backup_name)
            print(f"Backup created: {backup_name}")
        os.rename(oldname, newname)
        print(f"Renamed {oldname} to {newname}")
    else:
        print(f"Error: {oldname} does not exist")


def modify_permissions(filename, permissions):
    if os.path.exists(filename):
        os.chmod(filename, permissions)
        print(f"Permissions of {filename} changed to {oct(permissions)}")
    else:
        print(f"Error: {filename} does not exist")


def modify_ownership(filename, owner, group):
    if os.path.exists(filename):
        shutil.chown(filename, user=owner, group=group)
        print(f"Ownership of {filename} changed to {owner}:{group}")
    else:
        print(f"Error: {filename} does not exist")


def create_directory(directories):
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory {directory}")


def display_metadata(filename):
    if os.path.exists(filename):
        stats = os.stat(filename)
        print(f"Metadata for {filename}:")
        print(f"Size: {stats.st_size} bytes")
        print(f"Created: {time.ctime(stats.st_ctime)}")
        print(f"Modified: {time.ctime(stats.st_mtime)}")
        print(f"Permissions: {oct(stats.st_mode & 0o777)}")
        print(f"Owner: {stats.st_uid}, Group: {stats.st_gid}")
    else:
        print(f"Error: {filename} does not exist")


def compress_directory(directory, output):
    shutil.make_archive(output, 'zip', directory)
    print(f"Compressed {directory} to {output}.zip")


def create_with_content(dir_content_map):
    for directory, contents in dir_content_map.items():
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory {directory}")
        for content in contents:
            content_path = Path(directory) / content
            if content_path.suffix:
                create_file([str(content_path)])
            else:
                create_directory([str(content_path)])


def parse_args(args):
    command_map = {
        'create': 'c',
        'add': 'a',
        'change': 'ch',
        'permissions': 'p',
        'ownership': 'o',
        'directory': 'd',
        'info': 'i',
        'compress': 'z',
        'create_with_content': 'cc'
    }
    parsed_args = {'command': None, 'filenames': [], 'content': None, 'newname': None,
                   'backup': False, 'permissions': None, 'owner': None, 'group': None, 'output': None, 'dir_content_map': {}}
    if len(args) >= 1:
        command = args[0]
        for long_cmd, short_cmd in command_map.items():
            if command == long_cmd or command == f"-{short_cmd}":
                parsed_args['command'] = long_cmd
                break
        if not parsed_args['command']:
            print("Unknown command")
            sys.exit(1)

        if parsed_args['command'] in ['create', 'directory']:
            parsed_args['filenames'] = args[1:]
        elif parsed_args['command'] == 'add':
            parsed_args['filenames'] = [args[1]]
            parsed_args['content'] = ' '.join(args[2:])
        elif parsed_args['command'] == 'change':
            parsed_args['filenames'] = [args[1]]
            parsed_args['newname'] = args[2]
            parsed_args['backup'] = '--backup' in args
        elif parsed_args['command'] == 'permissions':
            parsed_args['filenames'] = [args[1]]
            parsed_args['permissions'] = args[2]
        elif parsed_args['command'] == 'ownership':
            parsed_args['filenames'] = [args[1]]
            parsed_args['owner'] = args[2]
            parsed_args['group'] = args[3]
        elif parsed_args['command'] == 'info':
            parsed_args['filenames'] = [args[1]]
        elif parsed_args['command'] == 'compress':
            parsed_args['filenames'] = [args[1]]
            parsed_args['output'] = args[2][len("--output="):]
        elif parsed_args['command'] == 'create_with_content':
            current_dir = None
            contents = []
            i = 1
            while i < len(args):
                arg = args[i]
                if arg in ['-cc', 'create_with_content']:
                    if current_dir is not None:
                        parsed_args['dir_content_map'][current_dir] = contents
                    current_dir = args[i + 1]
                    contents = []
                    i += 2
                elif arg == '-c' or arg == '-d':
                    j = i + 1
                    while j < len(args) and not args[j].startswith('-'):
                        contents.append(args[j])
                        j += 1
                    i = j
                else:
                    i += 1
            if current_dir is not None:
                parsed_args['dir_content_map'][current_dir] = contents
        else:
            print("Unknown command")
            sys.exit(1)
    else:
        print("Usage: manufacture <command> <filename> [content]")
        sys.exit(1)
    return parsed_args


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: manufacture <command> <filename> [content]\n"
            "Commands:\n"
            "  create, -c <filename>... : Create files\n"
            "  add, -a <filename> <content> : Add content to a file\n"
            "  change, -ch <oldname> <newname> [--backup] : Rename file\n"
            "  permissions, -p <filename> <permissions> : Change file permissions\n"
            "  ownership, -o <filename> <owner> <group> : Change file ownership\n"
            "  directory, -d <dirname>... : Create directories\n"
            "  info, -i <filename> : Display file metadata\n"
            "  compress, -z <directory> --output=<output> : Compress directory\n"
            "  create_with_content, -cc -cc <dirname> -c <file>... -d <dirname>... : Create directories and add content\n"
        )
        sys.exit(1)

    parsed_args = parse_args(sys.argv[1:])
    command = parsed_args['command']
    filenames = parsed_args['filenames']
    content = parsed_args['content']
    newname = parsed_args['newname']
    backup = parsed_args['backup']
    permissions = parsed_args['permissions']
    owner = parsed_args['owner']
    group = parsed_args['group']
    output = parsed_args['output']
    dir_content_map = parsed_args['dir_content_map']

    if command == "create":
        create_file(filenames)
    elif command == "add":
        add_content(filenames[0], content)
    elif command == "change":
        change_file(filenames[0], newname, backup)
    elif command == "permissions":
        modify_permissions(filenames[0], int(permissions, 8))
    elif command == "ownership":
        modify_ownership(filenames[0], owner, group)
    elif command == "directory":
        create_directory(filenames)
    elif command == "info":
        display_metadata(filenames[0])
    elif command == "compress":
        compress_directory(filenames[0], output)
    elif command == "create_with_content":
        create_with_content(dir_content_map)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
