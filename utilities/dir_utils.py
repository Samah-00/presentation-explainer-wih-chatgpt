import os

UPLOAD_FOLDER = '..\\uploads'
OUTPUT_FOLDER = '..\\outputs'


def get_files_list(folder):
    return os.listdir(folder)
