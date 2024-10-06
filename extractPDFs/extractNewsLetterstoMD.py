from pypdf import PdfReader
import os

def scan_for_files_ext(directory,extension):
  """Scans a directory and subdirectories for files with a '.md' extension and returns a list of their names without the extension.

  Args:
    directory: The directory to scan.

  Returns:
    A list of strings containing the names of the '.md' files without the extension.
  """
  out_files = []

  for root, dirs, files in os.walk(directory):
    for file in files:
      if file.endswith(extension):
        out_files.append(file[:-len(extension)])  # Remove the '.md' extension

  return out_files


def extractFileToText(pdf_file,text_file):
    reader = PdfReader(pdf_file)
    with open(text_file, 'w', encoding='utf-8') as f:
        for page in reader.pages:
            text = page.extract_text()
            f.write(text)

if __name__ == "__main__":
    # Example usage:
    directory_to_scan = "C:\\Users\\tom\\Documents\\Cozy\\Cozy_Newsletters_04-91"
    file_list = scan_for_files_ext(directory_to_scan,'.pdf')
    for file_name in file_list:
       pdf_file = f"{directory_to_scan}\\{file_name}.pdf"
       text_file = f"news_txt\\{file_name}.txt"
       extractFileToText(pdf_file,text_file)



