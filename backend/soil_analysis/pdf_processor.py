import pdfplumber

def extract(pdf_file):
    pdf_path = f'temp_{pdf_file.filename}'
    pdf_file.save(pdf_path)

    extracted_text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() + '\n'

    import os
    os.remove(pdf_path)

    return extracted_text
