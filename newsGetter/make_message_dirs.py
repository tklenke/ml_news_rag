#make message dirs
import os

# ---  CONSTANTS
msgs_dir = "msgs"
filename = "A_ids.txt"  # Replace with your actual file name

def count_first_characters(filename):
  """Counts the occurrences of the first character in each line of a file.

  Args:
    filename: The name of the file to process.

  Returns:
    A tuple containing a list of characters and their counts, and the total number of lines read.
  """

  character_counts = {}
  total_lines = 0

  with open(filename, 'r') as file:
    for line in file:
        first_char = line[0]
        character_counts[first_char] = character_counts.get(first_char, 0) + 1
        total_lines += 1

  return character_counts, total_lines


def makethedirs(counts):
    """Creates directories for each character in the counts dictionary, nested within a "msgs" directory.

    Args:
    counts: A dictionary containing character counts.
    """

    # Create the "msgs" directory if it doesn't exist

    if not os.path.exists(msgs_dir):
        os.mkdir(msgs_dir)

  # Create the "a" directory for the numbers and characters if it doesn't exist
    a_dir = "aDig"
    sub_dir_path = os.path.join(msgs_dir, a_dir)
    if not os.path.exists(sub_dir_path):
        os.mkdir(sub_dir_path)

  # Create subdirectories for each letter within the "msgs" directory
    for char, count in counts.items():
        if char.isalpha():
            dir_name = char.upper()
            sub_dir_path = os.path.join(msgs_dir, dir_name)
            if not os.path.exists(sub_dir_path):
                os.mkdir(sub_dir_path)


counts, lines = count_first_characters(filename)

print("Character counts:")
for char, count in counts.items():
  print(f"{char}: {count}")

print(f"Total lines read: {lines}")

print(f"Making directories...")
makethedirs(counts)