import sqlite3

def analyze_letter_pairs(db_name='tanakh.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Créer une table pour stocker les occurrences de paires de lettres
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS letter_pair_occurrences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_letter TEXT NOT NULL,
            last_letter TEXT NOT NULL,
            occurrence_count INTEGER NOT NULL,
            UNIQUE(first_letter, last_letter)
        )
    """)
    conn.commit()

    # Récupérer tous les versets nettoyés
    cursor.execute("SELECT text_cleaned FROM verses WHERE text_cleaned IS NOT NULL AND text_cleaned != ''")
    cleaned_texts = cursor.fetchall()

    pair_counts = {}

    for (text,) in cleaned_texts:
        if len(text) >= 2:
            first_char = text[0]
            last_char = text[-1]
            pair = (first_char, last_char)
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    # Insérer ou mettre à jour les occurrences dans la nouvelle table
    for (first_letter, last_letter), count in pair_counts.items():
        cursor.execute("""
            INSERT INTO letter_pair_occurrences (first_letter, last_letter, occurrence_count)
            VALUES (?, ?, ?)
            ON CONFLICT(first_letter, last_letter) DO UPDATE SET
            occurrence_count = excluded.occurrence_count
        """, (first_letter, last_letter, count))
    
    conn.commit()
    conn.close()
    print("Analyse des occurrences de paires de lettres terminée.")

if __name__ == '__main__':
    db_file = '/home/ubuntu/tanakh-search-app/src/tanakh.db'
    analyze_letter_pairs(db_file)


