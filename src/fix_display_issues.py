#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger les problèmes d'affichage des versets hébreux
- Supprimer les doublons d'affichage
- Nettoyer le texte hébreu des symboles parasites
- Vérifier les traductions manquantes
"""

import sqlite3
import re
import json

def clean_hebrew_text(text):
    """
    Nettoie le texte hébreu en supprimant les symboles parasites
    """
    if not text:
        return text
    
    # Supprimer les caractères / parasites au milieu des mots
    cleaned = re.sub(r'(?<=[\u0590-\u05FF])/(?=[\u0590-\u05FF])', '', text)
    
    # Supprimer d'autres symboles parasites courants
    cleaned = re.sub(r'[^\u0590-\u05FF\u0020-\u007E\s\u200F\u200E]', '', cleaned)
    
    # Ajouter des espaces entre les mots hébreux si manquants (heuristique simple)
    # Cela suppose que les mots sont séparés par des caractères non-hébreux ou des espaces
    # et qu'il n'y a pas de ponctuation collée aux mots qui devrait rester collée.
    # Pour une correction plus précise, une analyse morphologique serait nécessaire.
    cleaned = re.sub(r'([\u0590-\u05FF])([\u0590-\u05FF])', r'\1 \2', cleaned)
    
    # Nettoyer les espaces multiples
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def analyze_database():
    """
    Analyse la base de données pour identifier les problèmes
    """
    conn = sqlite3.connect('tanakh.db')
    cursor = conn.cursor()
    
    # Vérifier la structure de la base
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables disponibles:", tables)
    
    # Analyser la table des versets
    cursor.execute("PRAGMA table_info(verses);")
    columns = cursor.fetchall()
    print("Colonnes de la table verses:", columns)
    
    # Compter les versets avec et sans traduction
    cursor.execute("SELECT COUNT(*) FROM verses WHERE translation_fr IS NOT NULL AND translation_fr != '';")
    with_translation = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM verses;")
    total_verses = cursor.fetchone()[0]
    
    print(f"Versets avec traduction: {with_translation}/{total_verses}")
    
    # Examiner quelques exemples de texte hébreu avec des problèmes
    cursor.execute("SELECT book, chapter, verse, text_cleaned FROM verses WHERE text_cleaned LIKE '%/%' LIMIT 10;")
    problematic_verses = cursor.fetchall()
    
    print("Exemples de versets avec des symboles parasites:")
    for book, chapter, verse, text in problematic_verses:
        ref = f"{book} {chapter}:{verse}"
        print(f"{ref}: {text}")
    
    conn.close()
    return {
        'total_verses': total_verses,
        'with_translation': with_translation,
        'problematic_count': len(problematic_verses)
    }

def fix_hebrew_text():
    """
    Corrige le texte hébreu dans la base de données
    """
    conn = sqlite3.connect('tanakh.db')
    cursor = conn.cursor()
    
    # Récupérer tous les versets
    cursor.execute("SELECT id, text_cleaned FROM verses;")
    verses = cursor.fetchall()
    
    fixed_count = 0
    for verse_id, text in verses:
        cleaned_text = clean_hebrew_text(text)
        if cleaned_text != text:
            cursor.execute("UPDATE verses SET text_cleaned = ? WHERE id = ?", (cleaned_text, verse_id))
            fixed_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"Texte hébreu corrigé pour {fixed_count} versets")
    return fixed_count

def check_missing_translations():
    """
    Identifie les versets sans traduction
    """
    conn = sqlite3.connect('tanakh.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT book, chapter, verse, text_cleaned 
        FROM verses 
        WHERE (translation_fr IS NULL OR translation_fr = '') 
        LIMIT 20
    """)
    
    missing = cursor.fetchall()
    conn.close()
    
    print(f"Exemples de versets sans traduction ({len(missing)} affichés):")
    for book, chapter, verse, text in missing:
        ref = f"{book} {chapter}:{verse}"
        print(f"{ref}: {text[:50]}...")
    
    return missing

def main():
    print("=== Analyse et correction des problèmes d'affichage ===")
    
    # Analyser la base de données
    stats = analyze_database()
    print(f"\nStatistiques: {stats}")
    
    # Corriger le texte hébreu
    print("\n=== Correction du texte hébreu ===")
    fixed_count = fix_hebrew_text()
    
    # Vérifier les traductions manquantes
    print("\n=== Vérification des traductions manquantes ===")
    missing = check_missing_translations()
    
    print(f"\nRésumé:")
    print(f"- {fixed_count} versets corrigés pour le texte hébreu")
    print(f"- {len(missing)} versets sans traduction identifiés")

if __name__ == "__main__":
    main()

