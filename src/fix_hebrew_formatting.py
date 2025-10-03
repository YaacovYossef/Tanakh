#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re
import os

def get_db_connection():
    """Obtient une connexion à la base de données SQLite."""
    db_path = os.path.join(os.path.dirname(__file__), "tanakh.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def clean_hebrew_text(text_raw):
    """
    Nettoie et formate le texte hébreu pour une meilleure lisibilité.
    """
    if not text_raw:
        return ""
    
    # Supprimer les références KJV au début
    text = re.sub(r'^KJV:[^|]*\|', '', text_raw)
    
    # Diviser le texte en mots individuels
    words = text.split()
    
    cleaned_words = []
    for word in words:
        # Supprimer les caractères de ponctuation et symboles parasites
        cleaned_word = re.sub(r'[/\|\.\:\;\,\!\?\(\)\[\]\{\}]', '', word)
        
        # Supprimer les caractères non-hébreux (sauf les voyelles)
        # Garder les lettres hébraïques (0x05D0-0x05EA) et les signes diacritiques (0x05B0-0x05C7)
        cleaned_word = re.sub(r'[^\u05D0-\u05EA\u05B0-\u05C7\u05F0-\u05F4]', '', cleaned_word)
        
        # Ajouter le mot nettoyé s'il n'est pas vide
        if cleaned_word.strip():
            cleaned_words.append(cleaned_word)
    
    # Joindre les mots avec des espaces
    return ' '.join(cleaned_words)

def update_hebrew_formatting():
    """
    Met à jour le formatage du texte hébreu dans la base de données.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer tous les versets
    cursor.execute("SELECT id, text_raw FROM verses")
    verses = cursor.fetchall()
    
    print(f"Traitement de {len(verses)} versets...")
    
    updated_count = 0
    for verse in verses:
        verse_id = verse['id']
        text_raw = verse['text_raw']
        
        # Nettoyer le texte hébreu
        text_cleaned = clean_hebrew_text(text_raw)
        
        # Mettre à jour la base de données
        cursor.execute(
            "UPDATE verses SET text_cleaned = ? WHERE id = ?",
            (text_cleaned, verse_id)
        )
        
        updated_count += 1
        if updated_count % 100 == 0:
            print(f"Mis à jour {updated_count} versets...")
    
    conn.commit()
    conn.close()
    
    print(f"Formatage terminé. {updated_count} versets mis à jour.")

def test_formatting():
    """
    Teste le formatage sur quelques versets pour vérifier le résultat.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tester sur quelques versets
    cursor.execute("""
        SELECT book, chapter, verse, text_raw, text_cleaned 
        FROM verses 
        WHERE book='Ps' AND chapter=20 
        LIMIT 3
    """)
    
    test_verses = cursor.fetchall()
    
    print("\n=== Test du formatage ===")
    for verse in test_verses:
        print(f"\n{verse['book']} {verse['chapter']}:{verse['verse']}")
        print(f"Texte brut: {verse['text_raw'][:100]}...")
        print(f"Texte nettoyé: {verse['text_cleaned']}")
    
    conn.close()

if __name__ == "__main__":
    print("Correction du formatage du texte hébreu...")
    update_hebrew_formatting()
    test_formatting()
    print("\nTerminé!")

