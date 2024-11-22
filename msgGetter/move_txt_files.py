import os
import shutil

def move_txt_files(source_dir, target_dir):
  """Moves all .txt files from source directory to target directory.

  Args:
    source_dir: The top directory to search for .txt files.
    target_dir: The top directory to move the .txt files to.
  """

  for root, _, files in os.walk(source_dir):
    for file in files:
      if file.endswith(".txt"):
        source_file = os.path.join(root, file)
        target_file = os.path.join(target_dir, os.path.relpath(root, source_dir), file)
        target_dir_path = os.path.dirname(target_file)

        # Create the target directory if it doesn't exist
        os.makedirs(target_dir_path, exist_ok=True)
        print(f"moving {source_file} {target_file}")

        shutil.move(source_file, target_file)

# Example usage:
source_dir = r"../data/msgs"
target_dir = r"../data/msgs_filtered"

move_txt_files(source_dir, target_dir)