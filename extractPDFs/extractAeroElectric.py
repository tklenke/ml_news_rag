from pypdf import PdfReader
import os

INPUT_FILE = "/mnt/c/Users/tom/Documents/Cozy/aeroelectric_connection.pdf"
OUTPUT_DIR = './data/aeroelectric/'

if __name__ == "__main__":
    reader = PdfReader(INPUT_FILE)
    numPage = 0
    for page in reader.pages:
        numPage += 1
        text_file = OUTPUT_DIR + f"page{numPage}.txt"
        print(f"file:{text_file}")
        with open(text_file, 'w', encoding='utf-8') as f:
            text = page.extract_text()
            f.write(text)
            f.close()


