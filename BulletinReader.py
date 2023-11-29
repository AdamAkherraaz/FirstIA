import pandas as pd
import pytesseract
from PIL import Image
import nltk


df_hommes = pd.read_csv('NomHomme.csv')
df_femmes = pd.read_csv('NomFemme.csv')


ensemble_hommes = set(df_hommes['preusuel'].str.upper())
ensemble_femmes = set(df_femmes['preusuel'].str.upper())

def extract_text_from_image(file_path):
    try:
        return pytesseract.image_to_string(Image.open(file_path))
    except Exception as e:
        print(f"Erreur lors de la lecture de l'image: {e}")
        return None


def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier texte: {e}")
        return None


def extract_names(text, df_hommes, df_femmes):
    nltk.download('names', quiet=True)
    from nltk.corpus import names
    words = set(text.upper().split())
    names_list = set(word for word in words if word.capitalize() in names.words())
    result = []

    for name in names_list:
        name_title = name.title()
        if name in ensemble_hommes and name in ensemble_femmes:
          
            somme_homme = df_hommes[df_hommes['preusuel'] == name_title]['nombre'].sum()
            somme_femme = df_femmes[df_femmes['preusuel'] == name_title]['nombre'].sum()

            if somme_homme > somme_femme:
                result.append(f"{name_title} & Homme")
            else:
                result.append(f"{name_title} & Femme")
        elif name in ensemble_hommes:
            result.append(f"{name_title} & Homme")
        elif name in ensemble_femmes:
            result.append(f"{name_title} & Femme")
        else:
            result.append("Rien ne match")

    return result



def process_file(file_path, df_hommes, df_femmes):
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        text = extract_text_from_image(file_path)
    elif file_path.lower().endswith('.txt'):
        text = extract_text_from_txt(file_path)
    else:
        print("Format de fichier non pris en charge.")
        return None

    if text:
        return extract_names(text, df_hommes, df_femmes)
    else:
        print("Aucun texte trouvé ou fichier illisible.")
        return None



def main():
    file_path = input("Entrez le chemin du fichier: ")
    names = process_file(file_path, df_hommes, df_femmes)
    if names:
        print("Prénoms trouvés:")
        for name in names:
            print(name)
    else:
        print("Aucun prénom trouvé.")


if __name__ == "__main__":
    main()
