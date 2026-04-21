from pypdf import PdfReader

def load_pdfs(folder_path):
    documents = []

    import os
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            reader = PdfReader(f"{folder_path}/{file}")
            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""

            documents.append({
                "filename": file,
                "text": text
            })

    return documents