import sys
import os
from utils import (
    extract_json_from_term_sheet,
    json_list_to_csv,
    process_pdf_directory,
    count_pdf_files,
)


def main(input_path, output_path):
    all_texts = process_pdf_directory(input_path)
    json_list = []
    count = 1
    for text in all_texts:
        json_list.append(extract_json_from_term_sheet(text))
        print(f"Analyzed text: {count}/{count_pdf_files(input_path)}")
        count += 1
    json_list_to_csv(json_list, output_path)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print(f"Analyzing files in {input_path}")
        main(input_path,output_path)
    else:
        print("Please provide both the input and output directory paths as arguments.")