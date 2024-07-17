import os


def is_tiff(file):
    """
    Returns a boolean indicating if a file is a tiff image
    
    Parameters:
        file: (Relative) Path to file wanting to check if a tiff
    """
    filename, file_extension = os.path.splitext(file)
    
    file_extension = file_extension.lower()
    
    return file_extension.find(".tif") == 0


def get_tiffs_from_folder(tiff_folder):
    """
    Return all the tiffs files from the tiff_folder
    
    Parameters:
        file: (Relative) Path to folder wanting to check
    """
    if not os.path.isdir(tiff_folder):
        raise Exception(f"Folder {tiff_folder} Doesn't Exist")

    files = os.listdir(tiff_folder)

    tiff_files = []

    for file in files:
        if is_tiff(file):
            file = f"{tiff_folder}{file}"
            tiff_files.append(file)

    return tiff_files



