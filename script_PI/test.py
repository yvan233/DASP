import os
def _get_all_files_in_local_dir(local_dir):
    all_files = list()

    for root, dirs, files in os.walk(local_dir, topdown=True):
        for file in files:
            filename = os.path.join(root, file)
            all_files.append(filename)

    return all_files

print(_get_all_files_in_local_dir('./DASP'))