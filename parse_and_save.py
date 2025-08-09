import os
import json
from doc_parser import DocumentParser

def parse_and_save(input_file: str):
    parser = DocumentParser()
    result = parser.parse_document(input_file)
    
    # Create output file path (same folder, .json extension)
    folder = os.path.dirname(input_file)
    base = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(folder, f"{base}_output.json")
    
    # Save result as JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    # Example usage: replace with your .docx file path
    input_docx = "c:\\Users\\Sachin suresh\\Desktop\\Projects\\ML\\ai-engineer-task-Sachin-0001\\example.docx"
    parse_and_save(input_docx)