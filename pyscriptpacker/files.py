import os


def get_file_content(file):
    '''
    Get the content of given file.

    Args:
        file (string): The full path of the file.

    Returns:
        string: The whole content of the given file.
    '''
    content = ''
    with open(file, 'r') as file_data:
        content = file_data.read()
    return content


def get_file_paths(directory):
    '''
    Return all file paths of the particular directory.

    Args:
        directory (string): The directory to query all the file paths.
    '''
    file_paths = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_paths.append(file_path)
    return file_paths
