import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import time

# Mapping manuel et vérifié des noms de livres OSIS vers les codes Mechon-Mamre
# Basé sur l'observation des URLs sur mechon-mamre.org/f/ft/ft0.htm et la navigation manuelle.
BOOK_MAP = {
    "Gen": "ft01", "Exod": "ft02", "Lev": "ft03", "Num": "ft04", "Deut": "ft05",
    "Josh": "ft06", "Judg": "ft07", 
    "1Sam": "ft08a", "2Sam": "ft08b", 
    "1Kgs": "ft09a", "2Kgs": "ft09b",
    "Isa": "ft10", "Jer": "ft11", "Ezek": "ft12", 
    "Hos": "ft13", "Joel": "ft14", "Amos": "ft15",
    "Obad": "ft16", "Jonah": "ft17", "Mic": "ft18", 
    "Nah": "ft19", "Hab": "ft20", "Zeph": "ft21",
    "Hag": "ft22", "Zech": "ft23", "Mal": "ft24",
    "1Chr": "ft25a", "2Chr": "ft25b",
    "Ps": "ft26", "Job": "ft27", "Prov": "ft28", 
    "Ruth": "ft29", "Song": "ft30", "Eccl": "ft31",
    "Lam": "ft32", "Esth": "ft33", "Dan": "ft34", 
    "Ezra": "ft35a", "Neh": "ft35b"
}

def get_translation_from_mechon_mamre(book_osis_id, chapter_num, verse_num):
    book_code = BOOK_MAP.get(book_osis_id)
    if not book_code:
        return None

    if book_osis_id == "Ps":
        url = f"https://mechon-mamre.org/f/ft/{book_code}{chapter_num:02d}.htm"
    else:
        url = f"https://mechon-mamre.org/f/ft/{book_code}{chapter_num:02d}.htm"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP d'erreur
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Chercher spécifiquement la structure à deux colonnes (hébreu | français)
    # Les versets sont souvent dans des <tr> avec deux <td> enfants
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 2: 
            hebrew_col = tds[0]
            french_col = tds[1]
            
            # Vérifier si la colonne hébraïque contient le numéro de verset en gras
            # Le numéro de verset hébreu est dans un <b> tag, mais il peut y avoir d'autres <b> tags
            # On cherche le <b> tag qui contient uniquement le numéro de verset
            # Le numéro de verset hébreu est souvent suivi d'un espace insécable (&nbsp;)
            # La balise <b> contient le numéro de verset hébreu (ex: א, ב, ג...) et non le numéro numérique.
            # Le numéro numérique est dans la colonne française.
            
            # On cherche le <td> de la colonne française qui contient le numéro de verset en gras
            b_tag_french = french_col.find('b', string=str(verse_num))
            
            if b_tag_french:
                # Extraire le texte de la colonne française
                french_text = french_col.get_text(separator=' ', strip=True)
                # Supprimer le numéro de verset au début de la traduction française s'il est présent
                french_text = re.sub(r'^\d+\s*', '', french_text)
                return french_text
    
    # Fallback pour les livres avec une structure à une seule colonne (numéro de verset en gras dans le même td que la traduction)
    # Cette logique est moins précise mais peut fonctionner pour d'autres formats
    for td in soup.find_all('td', valign='top'):
        b_tag = td.find('b')
        if b_tag and b_tag.text == str(verse_num):
            text_parts = []
            for content in td.contents:
                if isinstance(content, str):
                    text_parts.append(content.strip())
                elif content.name != 'b': # Ignorer le tag <b> du numéro de verset
                    text_parts.append(content.get_text().strip())
            
            translation = ' '.join(text_parts).strip()
            translation = re.sub(r'^\d+\s*', '', translation) # Supprimer le numéro de verset au début
            return translation

    return None

def update_database_with_translations():
    db_file = '/home/ubuntu/tanakh-search-app/src/tanakh.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Sélectionner les versets qui n'ont pas encore de traduction française
    cursor.execute("SELECT id, book, chapter, verse FROM verses WHERE translation_fr IS NULL OR translation_fr = ''")
    verses_to_update = cursor.fetchall()

    print(f"Found {len(verses_to_update)} verses to update with French translation.")

    for i, verse_data in enumerate(verses_to_update):
        verse_id, book, chapter, verse = verse_data
        
        translation = get_translation_from_mechon_mamre(book, chapter, verse)
        
        if translation:
            cursor.execute("UPDATE verses SET translation_fr = ? WHERE id = ?", (translation, verse_id))
            if (i + 1) % 100 == 0: # Commit toutes les 100 mises à jour pour éviter une transaction trop longue
                conn.commit()
                print(f"Updated {i+1} verses. Last updated: {book} {chapter}:{verse}")
        else:
            print(f"Could not find translation for {book} {chapter}:{verse}")
        
        time.sleep(0.1) # Petite pause pour ne pas surcharger le serveur

    conn.commit()
    conn.close()
    print("Database update with French translations complete.")

if __name__ == '__main__':
    update_database_with_translations()


