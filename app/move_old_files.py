import os
import shutil


def move_old_files(source_directories_array, destination_directories_array):
    number_of_folders = len(source_directories_array)
    for i in range(number_of_folders):
        source = source_directories_array[i]
        if not os.path.exists(source):
            continue
        destination = destination_directories_array[i]
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        files = os.listdir(source)
        for file in files:
            path_to_file = os.path.join(source, file)
            # !will overwrite if file already exists in /export directory
            dest_path_to_file = os.path.join(destination, file)
            shutil.move(path_to_file, dest_path_to_file)


def move_old_input_files(source_directory, destination_directory):
    print(source_directory)

    files = os.listdir(source_directory)
    print(files)
    for file in files:
        print('moving file: ', file)
        path_to_file = os.path.join(source_directory, file)
        # !will overwrite if file already exists in /export directory
        dest_path_to_file = os.path.join(destination_directory, file)
        os.makedirs(os.path.dirname(dest_path_to_file), exist_ok=True)
        if os.path.isfile(path_to_file):
            shutil.move(path_to_file, dest_path_to_file)
            print('Moved:', file)
    print('\nInput file(s) moved to /old_input_files/.. directory')

