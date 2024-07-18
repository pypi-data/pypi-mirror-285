import os
import shutil
import hashlib

def get_file_list(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            files.append(os.path.join(root, file))

    return file_list

def get_dir_list(directory, relative=True):
    dir_list = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            if relative:
                dir_list.append(dir)
            else:
                dir_list.append(os.path.join(root, dir))

    return dir_list


def get_files_by_extension(directory, extensions, relative=True):
    file_list = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Get the file extension
            file_ext = os.path.splitext(file)[1].lower()

            for ext in extensions:
                if ext.casefold() == file_ext.casefold():
                    if relative:
                        file_list.append(file)
                    else:
                        file_list.append(os.path.join(root, file))

    return file_list

def get_files_containing_string(directory, string):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if string.casefold() in file.casefold():
                file_list.append(file)

    return file_list


def get_dirs_containing_string(directory, string, relative=True):
    dir_list = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            if string.casefold() in dir.casefold():
                if relative:
                    dir_list.append(dir)
                else:
                    dir_list.append(os.path.join(root, dir))

    return dir_list

def write_list_to_file(file_name, lines):
    with open(file_name, 'w') as file:
        for line in lines:
            file.write(line + '\n')

def read_list_from_file(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]


def directory_contains_directory(directory, subdirectory):
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            if subdirectory.casefold() in dir.casefold():
                return True
    return False

def directory_contains_file(directory, filename):
    for _, _, files in os.walk(directory):
        for file in files:
            if filename.casefold() in file.casefold():
                return True
    return False

def directory_contains_file_with_extension(directory, extension):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if extension.casefold() in os.path.splitext(file)[1].casefold():
                return True
    return False

def create_directory(directory_path):
    os.makedirs(directory_path, exist_ok=True)

def create_subdirectory(parent_dir, subdirectory_name):
    subdirectory_path = os.path.join(parent_dir, subdirectory_name)
    os.makedirs(subdirectory_path, exist_ok=True)

def copy_file(src_file_path, dest_file_path):
    shutil.copy2(src_file_path, dest_file_path)

def directory_exists(directory_path):
    return os.path.exists(directory_path) and os.path.isdir(directory_path)

def delete_directory(directory_path):
    if os.path.exists(directory_path):
        if os.path.isdir(directory_path):
            shutil.rmtree(directory_path)
        else:
            print("The path is not a directory!")
    else:
        print("The directory does not exist!")

def get_file_extension(file_path):
    return os.path.splitext(file_path)[1].lower()

def print_list(list):
    for item in list:
        print(item)

def get_md5_hash(file_path):
    with open(file_path, 'rb') as file:
        md5_hash = hashlib.md5(file.read()).hexdigest()
    return md5_hash

def get_file_name(file_path):
    return os.path.basename(file_path)
