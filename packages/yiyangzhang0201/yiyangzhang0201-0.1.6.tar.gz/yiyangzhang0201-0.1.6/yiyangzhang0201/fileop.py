import os
import shutil


def get_subfolders(parent_path):
    # Get the name of the parent folder
    parent_folder = parent_path
    # List to store the names of subfolders
    subfolders = []
    # Iterate over all the items in the parent folder
    for item in os.listdir(parent_folder):
        # Create full path to the item
        item_path = os.path.join(parent_folder, item)
        # Check if the item is a directory and add it to the list
        if os.path.isdir(item_path):
            subfolders.append(item)
    # Now subfolders list contains the names of all subfolders
    return subfolders


def get_files(folder_names):
    # Specify the path to the folder
    folder_path = folder_names
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # List to store the names of files
    files = []

    # Iterate over all the items in the folder
    for item in os.listdir(folder_path):
        # Create the full path to the item
        item_path = os.path.join(folder_path, item)
        # Check if the item is a file and append it to the list
        if os.path.isfile(item_path):
            files.append(item)

    # The 'files' list now contains the names of all files in the folder
    return files


def create_new_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def copy_file(file_path, new_fold):
    if not os.path.exists(new_fold):
        os.makedirs(new_fold)
    shutil.copy(file_path, new_fold)
