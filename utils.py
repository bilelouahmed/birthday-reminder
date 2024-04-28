from datetime import datetime


def timestamp_to_date(timestamp):
    """
    Convert a Unix timestamp to a European format date string.

    Parameters:
        timestamp (int): Unix timestamp

    Returns:
        str: European format date string
    """
    return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")


def read_file_list(file_name: str = "whitelist.txt"):
    with open(file_name, "r") as file:
        lines = file.readlines()

    ids = []

    for line in lines:
        cleaned_line = line.strip()
        ids.append(cleaned_line)

    return ids
