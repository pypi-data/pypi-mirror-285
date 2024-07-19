import os

def find_small_files(directory, size_limit):
    small_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) < size_limit:
                small_files.append(file_path)
    return small_files

def find_large_files(directory, size_limit):
    large_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) > size_limit:
                large_files.append(file_path)
    return large_files
  
