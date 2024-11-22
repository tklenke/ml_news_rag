import os

#Scans a directory and subdirectories for files
#Args:      directory: The directory to scan.
#Returns:   A list of strings containing the paths of all the files
def get_filepaths_list(directory):
    md_files = []

    if not os.path.exists(directory):
        print(f" Err: Directory {directory} does not exist.")
    else:
        for root, dirs, files in os.walk(directory):
            for name in files:
                md_files.append(os.path.join(root, name))

    return md_files

#Reads ids from a file into a list, removing trailing carriage returns and linefeeds.
#Args:    filename: The name of the file to read.
#Returns:   A list of strings, each containing a line from the file 
#           with trailing carriage returns and linefeeds removed.
def get_ids_list_from_file(filename):
    with open(filename, 'r') as f:
        lines = [line.rstrip() for line in f]
    f.close()
    return lines


#given a full path, return the filename without extension
def get_id_from_path(path):
    filename = path.split("/")[-1]

    # Split the filename based on the last dot (.)
    parts = filename.rsplit(".", 1)

    # Check if there's only one part (no extension)
    if len(parts) == 1:
        return filename
    # Otherwise, return the part before the dot
    else:
        return parts[0]

if __name__ == "__main__":
    MSG_DIR = r"../data/msgs"

    files = get_filepaths_list(MSG_DIR)

    for file in files:
        print(f"{file}")