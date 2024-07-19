import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS


def get_image_dates(filepath:str):
    """
    Extracts the creation date from an image file's EXIF data.

    Parameters:
    filepath (str): The path to the image file.

    Returns:
    datetime: The creation date of the image if found, otherwise None.

    Raises:
    Exception: If an error occurs during the extraction process, it will print an error message.
    """
    try:
        image = Image.open(filepath)
        exif_data = image._getexif()

        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'DateTimeOriginal':
                    creation_date = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                    return creation_date
    except Exception as e:
        print(f"An error occurred with file {filepath}: {e}")
    return None


def list_image_files(dirpath:str, extensions:list = ['.jpg', '.jpeg']):
    """
    Lists all image files in a directory and its subdirectories with specified extensions.

    Parameters:
    dirpath (str): The root directory to search for image files.
    extensions (list): A list of file extensions to include in the search. Defaults to ['.jpg', '.JPEG', '.jpeg', '.JPG'].

    Returns:
    list: A list of file paths that match the specified extensions.
    """
    file_paths = []
    for root, _, files in os.walk(dirpath):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                file_paths.append(os.path.join(root, file))
    return file_paths


def group_images_by_date(filepaths: list):
    """
    Groups image files by their creation dates.

    This function takes a list of image file paths, extracts the creation date for each image,
    and groups the images by these dates. The grouped images are stored in a dictionary where 
    the keys are formatted creation dates and the values are lists of file paths that correspond
    to those dates.

    Parameters:
    filepaths (list): A list of file paths to the image files.

    Returns:
    dict: A dictionary where keys are formatted creation dates (as strings) and values are lists 
          of file paths that have those creation dates.

    Example:
    >>> filepaths = ['/path/to/image1.jpg', '/path/to/image2.jpg']
    >>> group_images_by_date(filepaths)
    {
        '2023-01-01 12:00:00': ['/path/to/image1.jpg'],
        '2023-01-02 13:00:00': ['/path/to/image2.jpg']
    }
    """
    date_dict = {}

    for filepath in filepaths:
        creation_date = get_image_dates(filepath)
        if creation_date:
            formatted_date = creation_date.strftime('%Y-%m-%d %H:%M:%S')
            if formatted_date not in date_dict:
                date_dict[formatted_date] = []
            date_dict[formatted_date].append(filepath)

    return date_dict


def filter_keys_with_multiple_files(image_date_dict:dict):
    """
    Filters and returns the keys from the image_date_dict that have multiple file paths.

    This function is used to detect duplicates by identifying keys (formatted creation dates)
    that have more than one file path associated with them in the provided dictionary.

    Parameters:
    image_date_dict (dict): A dictionary where keys are formatted creation dates (as strings) 
                            and values are lists of file paths that correspond to those dates.

    Returns:
    list: A list of keys (formatted creation dates) that have multiple file paths, indicating duplicates.

    Example:
    >>> image_date_dict = {
    >>>     '2023-01-01 12:00:00': ['/path/to/image1.jpg', '/path/to/image1_duplicate.jpg'],
    >>>     '2023-01-02 13:00:00': ['/path/to/image2.jpg']
    >>> }
    >>> filter_keys_with_multiple_files(image_date_dict)
    ['2023-01-01 12:00:00']
    """
    return [key for key, value in image_date_dict.items() if len(value) > 1]


def extract_two_dirs_and_filename(filepaths:list):
    """
    Extracts the last two subdirectories and the filename from a list of file paths.

    This function processes a list of file paths, extracts the last two subdirectories and 
    the filename from each path, and returns a dictionary where the keys are tuples 
    containing the two subdirectories and the filename (or fewer components if not enough 
    subdirectories are present), and the values are the full file paths.

    Parameters:
    filepaths (list): A list of file paths to process.

    Returns:
    dict: A dictionary where keys are tuples of (subdir_1, subdir_2, filename) or fewer
          components, and values are the corresponding full file paths.

    Example:
    >>> filepaths = [
    >>>     '/path/to/subdir1/file1.jpg',
    >>>     '/another/path/to/subdir2/file2.jpg',
    >>>     '/file3.jpg'
    >>> ]
    >>> extract_two_dirs_and_filename(filepaths)
    {
        ('to', 'subdir1', 'file1.jpg'): '/path/to/subdir1/file1.jpg',
        ('to', 'subdir2', 'file2.jpg'): '/another/path/to/subdir2/file2.jpg',
        ('file3.jpg',): '/file3.jpg'
    }
    """
    extracted = {}
    for filepath in filepaths:
        parts = filepath.split(os.sep)
        if len(parts) >= 3:
            key = (parts[-3], parts[-2], parts[-1])
        elif len(parts) == 2:
            key = (parts[-2], parts[-1])
        elif len(parts) == 1:
            key = (parts[-1],)
        else:
            continue  # Skip empty or invalid file paths
        extracted[key] = filepath
    return extracted