
import requests
from bs4 import BeautifulSoup
import sqlite3
import re

def get_translation_from_mechon_mamre(book_name, chapter_num):
    # Mapping des noms de livres pour correspondre aux URL de Mechon-Mamre
    book_map = {
        "Gen": "ft01", "Exod": "ft02", "Lev": "ft03", "Num": "ft04", "Deut": "ft05",
        "Josh": "ft06", "Judg": "ft07", "1Sam": "ft08", "2Sam": "ft09", "1Kgs": "ft10", "2Kgs": "ft11",
        "Isa": "ft12", "Jer": "ft13", "Ezek": "ft14", "Hos": "ft15", "Joel": "ft16", "Amos": "ft17",
        "Obad": "ft18", "Jonah": "ft19", "Mic": "ft20", "Nah": "ft21", "Hab": "ft22", "Zeph": "ft23",
        "Hag": "ft24", "Zech": "ft25", "Mal": "ft26", "Ps": "ft27", "Prov": "ft28", "Job": "ft29",
        "Song": "ft30", "Ruth": "ft31", "Lam": "ft32", "Eccl": "ft33", "Esth": "ft34", "Dan": "ft35",
        "Ezra": "ft36", "Neh": "ft37", "1Chr": "ft38", "2Chr": "ft39"
    }

    mechon_mamre_book_code = book_map.get(book_name)
    if not mechon_mamre_book_code:
        print(f"Livre non trouvé dans le mapping Mechon-Mamre: {book_name}")
        return {}

    url = f"https://mechon-mamre.org/f/ft/{mechon_mamre_book_code}{chapter_num:02d}.htm"
    print(f"Scraping URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP d'erreur
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de l'URL {url}: {e}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    translations = {}

    # Les versets sont dans des balises <table>, chaque ligne (<tr>) contient un verset
    # La structure est généralement <td>Hébreu</td><td>Numéro du verset</td><td>Français</td>
    # Ou parfois <td>Numéro du verset</td><td>Hébreu</td><td>Français</td>
    # Ou <td>Hébreu</td><td>Français</td>

    # Chercher toutes les lignes de tableau qui contiennent les versets
    # On peut cibler les lignes qui contiennent des balises <small> pour les numéros de versets
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) >= 2:
            hebrew_text = ""
            french_text = ""
            verse_number = None

            # Heuristique pour trouver le numéro de verset, le texte hébreu et la traduction française
            # Les numéros de versets sont souvent en gras (<b>) ou en small (<i>) et sont des chiffres romains ou arabes
            # Le texte hébreu contient des caractères hébreux
            # Le texte français ne contient pas de caractères hébreux

            for col in cols:
                col_text = col.get_text(strip=True)
                if re.match(r'^\d+$', col_text) or re.match(r'^[א-ת]$', col_text): # Numéro de verset (arabe ou hébreu)
                    verse_number = col_text
                elif re.search(r'[\u0590-\u05FF]', col_text): # Contient des caractères hébreux
                    hebrew_text = col_text
                elif col_text and not re.search(r'[\u0590-\u05FF]', col_text): # Ne contient pas de caractères hébreux, probablement français
                    french_text = col_text
            
            if verse_number and french_text:
                # Nettoyer le numéro de verset si c'est une lettre hébraïque (ex: א -> 1)
                if verse_number in ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י']:
                    verse_number = str(['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'].index(verse_number) + 1)
                elif re.match(r'^[א-ת]$', verse_number):
                    # Pour les autres lettres, on peut ignorer ou trouver une conversion plus complexe
                    continue # Ignorer pour l'instant les versets avec des numéros de lettres complexes
                
                translations[int(verse_number)] = french_text

    return translations

def update_missing_translations():
    conn = sqlite3.connect('tanakh.db')
    cursor = conn.cursor()

    # Récupérer les versets sans traduction
    cursor.execute("SELECT id, book, chapter, verse, text_cleaned FROM verses WHERE translation_fr IS NULL OR translation_fr = '';")
    missing_verses = cursor.fetchall()

    print(f"\nDébut de la mise à jour des {len(missing_verses)} traductions manquantes...")

    updated_count = 0
    for verse_id, book, chapter, verse_num, text_cleaned in missing_verses:
        if book == "Esth" and chapter > 7: # Les chapitres 8, 9, 10 d'Esther sont souvent manquants
            # Mechon-Mamre ne semble pas avoir Esther 8-10
            continue

        # Récupérer les traductions pour le chapitre entier
        chapter_translations = get_translation_from_mechon_mamre(book, chapter)

        if verse_num in chapter_translations:
            translation = chapter_translations[verse_num]
            cursor.execute("UPDATE verses SET translation_fr = ? WHERE id = ?", (translation, verse_id))
            updated_count += 1
            # print(f"Mise à jour: {book} {chapter}:{verse_num}")

    conn.commit()
    conn.close()
    print(f"\nFin de la mise à jour. {updated_count} traductions ont été ajoutées/mises à jour.")

if __name__ == "__main__":
    update_missing_translations()


