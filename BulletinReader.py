from flask import Flask, request, send_file
import os
from PIL import Image
import pytesseract
import re
import csv
import pandas as pd

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Aucun fichier fourni", 400

    file = request.files['file']
    if file.filename == '':
        return "Aucun fichier sélectionné", 400

    if file and allowed_file(file.filename):
        img_path = './temp/' + file.filename
        file.save(img_path)
        return process_image(img_path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif', 'webp']

def process_image(img_path):
    text = extract_text_from_image(img_path)
    extracted_info = parse_extracted_text(text)
    
    if not extracted_info:
        return "Aucune donnée n'a été extraite. Vérifiez la sortie OCR et le regex.", 400

    csv_filename = './anonymized_grades.csv'
    save_to_csv(extracted_info, csv_filename)

    return send_file(csv_filename, as_attachment=True)


img_path = './assets/Bulletin_Scolaire.jpg.webp'

def extract_text_from_image(img_path):
    image = Image.open(img_path)
    text = pytesseract.image_to_string(image, lang='fra')
    return text

def parse_extracted_text(text):
    pattern = r'Matières\s+Moy\s+/20\s+Min\s+Max\s+Moy\s+Appréciations\n(.*?)(?=\nMoyenne générale|\Z)'
    subjects_text = re.search(pattern, text, re.DOTALL)
    
    if not subjects_text:
        return []

    subjects_text = subjects_text.group(1)
    subject_pattern = (
        r'(\w[\w\séèêàçûôîâÉÈÊÀÇÛÔÎÂ-]+(?: \(\d\))?)\s+'  
        r'(\d{1,2}[.,]\d{2})\s+'                        
        r'(\d{1,2}[.,]\d{2})\s+'                        
        r'(\d{1,2}[.,]\d{2})\s+'                         
        r'(\d{1,2}[.,]\d{2})\s+'                         
        r'(.+)'                                          
    )
    
    matches = re.findall(subject_pattern, subjects_text)
    extracted_info = [{'subject': match[0].strip(),
                       'student_average': match[1].replace(',', '.'),
                       'class_average': match[4].replace(',', '.'),
                       'comments': match[5].strip()} for match in matches]
    return extracted_info

def save_to_csv(data, filename):
    if not data:
        print("La liste des données est vide. Rien à enregistrer.")
        return
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=['subject', 'student_average', 'class_average', 'comments'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main(img_path):
    text = extract_text_from_image(img_path)
    print("Texte extrait par OCR :") 
    print(text)  

    extracted_info = parse_extracted_text(text)
    if not extracted_info:
        print("Aucune donnée n'a été extraite. Vérifiez la sortie OCR et le regex.")
        return

    save_to_csv(extracted_info, './anonymized_grades.csv')

    df = pd.DataFrame({'text_column': [text]})
    df.to_csv('./Bulletin.csv', index=False)

main(img_path)


main(img_path)

if __name__ =='__main__':
    app.run(debug=True)