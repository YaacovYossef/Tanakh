import xml.etree.ElementTree as ET
import sqlite3
import re
import os

def clean_hebrew_text(text):
    # Supprime les balises HTML et les entités XML comme &thinsp;
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[^;]+;', '', text)
    # Supprime les caractères non-hébreux (ponctuation, chiffres, diacritiques, cantillation)
    # Garde seulement les lettres hébraïques (U+05D0 à U+05EA)
    cleaned_text = re.sub(r'[^\u05D0-\u05EA]', '', text)
    return cleaned_text

def parse_osis_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Namespace pour OSIS XML
    ns = {'osis': 'http://www.bibletechnologies.net/2003/OSIS/namespace'}
    
    book_name = os.path.basename(file_path).replace('.xml', '')
    
    verses_data = []
    
    for chapter_elem in root.findall('.//osis:chapter', ns):
        chapter_num = chapter_elem.get('osisID')
        if chapter_num:
            # Extraire le numéro du chapitre de l'osisID (ex: Ps.1 -> 1)
            chapter_num = chapter_num.split('.')[-1]
            
            for verse_elem in chapter_elem.findall('.//osis:verse', ns):
                verse_num = verse_elem.get('osisID')
                if verse_num:
                    # Extraire le numéro du verset de l'osisID (ex: Ps.1.1 -> 1)
                    verse_num = verse_num.split('.')[-1]
                    
                    # Récupérer tout le texte contenu dans le verset, y compris les sous-éléments
                    verse_text_raw = ''.join(verse_elem.itertext())
                    
                    # Nettoyer le texte hébreu
                    cleaned_text = clean_hebrew_text(verse_text_raw)
                    
                    if cleaned_text:
                        verses_data.append({
                            'book': book_name,
                            'chapter': int(chapter_num),
                            'verse': int(verse_num),
                            'text_raw': verse_text_raw.strip(),
                            'text_cleaned': cleaned_text
                        })
    return verses_data

def create_database(db_name='tanakh.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text_raw TEXT NOT NULL,
            text_cleaned TEXT NOT NULL,
            first_char TEXT NOT NULL,
            last_char TEXT NOT NULL,
            translation_fr TEXT,
            commentary_rashi TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_verses(db_name, verses_data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for verse in verses_data:
        first_char = verse['text_cleaned'][0] if verse['text_cleaned'] else ''
        last_char = verse['text_cleaned'][-1] if verse['text_cleaned'] else ''
        cursor.execute("""
            INSERT INTO verses (book, chapter, verse, text_raw, text_cleaned, first_char, last_char, translation_fr, commentary_rashi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            verse["book"],
            verse["chapter"],
            verse["verse"],
            verse["text_raw"],
            verse["text_cleaned"],
            first_char,
            last_char,
            '', # Placeholder for translation_fr
            ''  # Placeholder for commentary_rashi
        ))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    xml_dir = '/home/ubuntu/OSHB-v.2.2'
    db_file = '/home/ubuntu/tanakh-search-app/src/tanakh.db'
    
    create_database(db_file)
    
    for filename in os.listdir(xml_dir):
        if filename.endswith('.xml') and filename != 'VerseMap.xml': # Ignorer VerseMap.xml
            file_path = os.path.join(xml_dir, filename)
            print(f"Parsing {filename}...")
            verses = parse_osis_xml(file_path)
            print(f"Found {len(verses)} verses in {filename}. Inserting into DB...")
            insert_verses(db_file, verses)
    
    print("Database creation and population complete.")
    
    # Vérification rapide
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM verses")
    count = cursor.fetchone()[0]
    print(f"Total verses in DB: {count}")
    
    cursor.execute("SELECT book, chapter, verse, text_raw FROM verses WHERE book = 'Ps' AND chapter = 20 AND verse = 2")
    psalm_20_2 = cursor.fetchone()
    if psalm_20_2:
        print(f"Psaumes 20:2 (raw): {psalm_20_2[3]}")
    
    cursor.execute("SELECT book, chapter, verse, text_cleaned, first_char, last_char FROM verses WHERE first_char = 'י' AND last_char = 'ב' LIMIT 5")
    test_search = cursor.fetchall()
    print("\nExemple de recherche (י...ב):")
    for row in test_search:
        print(f"  {row[0]} {row[1]}:{row[2]} - {row[3]} (First: {row[4]}, Last: {row[5]})")
    
    conn.close()



