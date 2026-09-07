# pyrefly: ignore [missing-import]
import PyPDF2
def pdf_text(pdf_file):
    try:
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error al extraer el texto del PDF: {e}")
        return None
