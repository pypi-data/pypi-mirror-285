import os


def get_current_project_name():
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)
    return project_name

def get_file_name_without_extension(file_path):
    file_name_with_extension = os.path.basename(file_path)
    file_name_without_extension = os.path.splitext(file_name_with_extension)[0]
    return file_name_without_extension
