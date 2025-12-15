import os
import re
import time
from googletrans import Translator
from PyPDF2 import PdfReader
from unidecode import unidecode

translator = Translator()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "tsp")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

MAX_CHARS = 4000  # SAFE LIMIT FOR GOOGLETRANS


def clean_filename(name):
    name = unidecode(name)
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    return name.replace(" ", "_").strip()


def translate_filename(filename):
    name, _ = os.path.splitext(filename)
    try:
        translated = translator.translate(name, dest="en").text
    except:
        translated = name
    return clean_filename(translated) + "_EN.txt"


def split_text(text, max_chars=MAX_CHARS):
    chunks = []
    current = ""

    for line in text.splitlines():
        if len(current) + len(line) < max_chars:
            current += line + "\n"
        else:
            chunks.append(current)
            current = line + "\n"

    if current:
        chunks.append(current)

    return chunks


def translate_text_safe(text):
    translated = ""
    chunks = split_text(text)

    for i, chunk in enumerate(chunks, 1):
        try:
            result = translator.translate(chunk, dest="en").text
            translated += result + "\n"
            time.sleep(0.5)  # prevent blocking
        except Exception as e:
            print(f"⚠️ Skipped chunk {i}: {e}")
            continue

    return translated


def process_pdf(pdf_path, output_path):
    reader = PdfReader(pdf_path)
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    translated_text = translate_text_safe(full_text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(translated_text)


print("🚀 Starting translation...\n")

for file in os.listdir(INPUT_FOLDER):
    input_path = os.path.join(INPUT_FOLDER, file)

    if not file.lower().endswith(".pdf"):
        continue

    print(f"🔄 Translating: {file}")

    output_filename = translate_filename(file)
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    process_pdf(input_path, output_path)

    print(f"✅ Saved as: {output_filename}\n")

print("🎉 ALL PDFs TRANSLATED SUCCESSFULLY!")
