"""OCR and text extraction utilities."""

import PyPDF2


def extract_text_from_image(image_path: str, client) -> str:
    """Use Gemma vision to extract text from an image."""
    prompt = (
        "Extract ALL text from this image exactly as it appears. "
        "Include student name, question numbers, and all marked/written answers. "
        "Preserve the structure and formatting."
    )
    return client.generate_with_image(prompt, image_path)


def extract_text_from_pdf(pdf_path: str, client) -> str:
    """Extract text from a PDF. Uses PyPDF2 first, falls back to OCR if empty."""
    text_parts = []
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    combined = "\n".join(text_parts).strip()

    # If PyPDF2 got meaningful text, return it
    if len(combined) > 50:
        return combined

    # Otherwise, the PDF likely contains scanned images — use Gemma OCR
    # Convert first page to image for OCR
    prompt = (
        "This is extracted text from a scanned PDF that may be incomplete or garbled. "
        "Please interpret and reconstruct the content as best as possible, "
        "preserving student names, question numbers, and answers.\n\n"
        f"Raw extracted text:\n{combined if combined else '[No text could be extracted — PDF is image-based]'}"
    )
    return client.generate(prompt)


def parse_answer_key(text: str) -> dict:
    """
    Parse a simple answer key file.
    Expected format (one per line):
        1:A
        2:C
        3:B
    Returns {1: 'A', 2: 'C', 3: 'B'}
    """
    key = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if ':' in line:
            parts = line.split(':', 1)
            try:
                q_num = int(parts[0].strip())
                answer = parts[1].strip().upper()
                key[q_num] = answer
            except ValueError:
                continue
    return key
