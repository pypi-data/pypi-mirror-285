import os
import glob
import random
import string

def generate_random_data(length):
    """
    Generates random data of a specified length.
    
    :param length: The length of the data to generate.
    :return: A bytes object containing random data.
    """
    return bytes(''.join(random.choices(string.printable, k=length)), 'utf-8')

def overwrite_file_with_random_data(file_path, passes=3):
    """
    Overwrites the file's content with random data multiple times before deletion.

    :param file_path: The path to the file to be overwritten and deleted.
    :param passes: The number of times to overwrite the file. Default is 3.
    """
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} is not a file.")
        return

    file_size = os.path.getsize(file_path)
    
    with open(file_path, 'r+b') as file:
        for i in range(passes):
            random_data = generate_random_data(file_size)
            file.seek(0)
            file.write(random_data)
            file.flush()
            os.fsync(file.fileno())
            print(f"Pass {i + 1}: File overwritten with random data.")

def delete_file(file_path):
    """
    Deletes the specified file.

    :param file_path: The path to the file to be deleted.
    """
    try:
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    except OSError as e:
        print(f"Error: {file_path} could not be deleted. {e}")

def shred_file(file_path, passes):
    """
    Shreds a single file by overwriting with random data and then deleting it.

    :param file_path: The path to the file to be shredded.
    :param passes: The number of passes to overwrite the file.
    """
    print(f'Shredding {file_path} now\n')
    overwrite_file_with_random_data(file_path, passes)
    delete_file(file_path)
    print(f'Done shredding {file_path}\n')

def shred_files_in_directory(folder_path, passes):
    """
    Shreds all files in a given directory by overwriting with random data and then deleting them.

    :param folder_path: The path to the directory containing files to be shredded.
    :param passes: The number of passes to overwrite the files.
    """
    pattern = os.path.join(folder_path, '**', '*')
    for file_path in glob.iglob(pattern, recursive=True):
        if os.path.isfile(file_path):
            shred_file(file_path, passes)
    print('Selected files have been shredded')

def main():
    input_path = input('Drag and drop the folder or file here:\n').strip().strip('"')
    passes = int(input('Enter the number of passes:\n'))
    
    if os.path.isdir(input_path):
        shred_files_in_directory(input_path, passes)
    elif os.path.isfile(input_path):
        shred_file(input_path, passes)
    else:
        print(f"Error: {input_path} is neither a file nor a directory.")
