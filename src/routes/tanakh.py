import sqlite3
import os
import json
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

tanakh_bp = Blueprint("tanakh", __name__)

def get_db_connection():
    """Obtient une connexion à la base de données SQLite."""
    db_path = os.path.join(os.path.dirname(__file__), "..", "tanakh.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
    return conn

def load_matched_names():
    """Load the matched names from the JSON file"""
    try:
        matched_names_path = os.path.join(os.path.dirname(__file__), "..", "matched_names.json")
        with open(matched_names_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@tanakh_bp.route("/search", methods=["POST"])
@cross_origin()
def search_verses():
    """Endpoint pour rechercher des versets par première et dernière lettre."""
    try:
        data = request.get_json()
        start_letter = data.get("start_letter", "")
        end_letter = data.get("end_letter", "")
        
        if not start_letter or not end_letter:
            return jsonify({"error": "Les lettres de début et de fin sont requises"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Recherche dans la base de données locale
        cursor.execute("""
            SELECT book, chapter, verse, text_raw, text_cleaned, first_char, last_char, translation_fr, commentary_rashi
            FROM verses 
            WHERE first_char = ? AND last_char = ?
            ORDER BY book, chapter, verse
        """, (start_letter, end_letter))
        
        results = cursor.fetchall()

        # Récupérer le nombre d'occurrences pour cette paire de lettres
        cursor.execute("SELECT occurrence_count FROM letter_pair_occurrences WHERE first_letter = ? AND last_letter = ?", (start_letter, end_letter))
        occurrence_row = cursor.fetchone()
        occurrence_count = occurrence_row["occurrence_count"] if occurrence_row else 0

        conn.close()
        
        # Convertir les résultats en format JSON
        verses_found = []
        for row in results:
            verse_data = {
                "book": row["book"],
                "chapter": row["chapter"],
                "verse": row["verse"],
                "reference": f'{row["book"]} {row["chapter"]}:{row["verse"]}',
                "text": row["text_cleaned"] or row["text_raw"],  # Utiliser text_cleaned en priorité
                "first_char": row["first_char"],
                "last_char": row["last_char"]
            }
            
            # Ajouter la traduction seulement si elle existe et n'est pas vide
            if row["translation_fr"] and row["translation_fr"].strip():
                verse_data["translation_fr"] = row["translation_fr"]
            
            # Ajouter le commentaire de Rashi seulement s'il existe et n'est pas vide
            if row["commentary_rashi"] and row["commentary_rashi"].strip():
                verse_data["rashi_commentary"] = row["commentary_rashi"]
                
            verses_found.append(verse_data)
        
        return jsonify({
            "results": verses_found,
            "count": len(verses_found),
            "search_criteria": {
                "start_letter": start_letter,
                "end_letter": end_letter
            },
            "occurrence_count": occurrence_count
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tanakh_bp.route("/search_by_name", methods=["POST"])
@cross_origin()
def search_by_name():
    """Endpoint pour rechercher des versets par nom hébreu."""
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        
        if not name:
            return jsonify({"error": "Le nom est requis"}), 400
        
        # Check if the name is a matched Hebrew name
        matched_names = load_matched_names()
        name_match = None
        for name_info in matched_names:
            if name.lower() == name_info['french_name'].lower():
                name_match = name_info
                break
        
        if not name_match:
            return jsonify({"error": "Nom non trouvé dans la base de données"}), 404
        
        # Extract the letter pair from the matched name
        letter_pair = name_match['letter_pair']
        first_letter = letter_pair[0]
        last_letter = letter_pair[1]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search for verses that start with first_letter and end with last_letter
        cursor.execute("""
            SELECT book, chapter, verse, text_raw, text_cleaned, first_char, last_char, translation_fr, commentary_rashi
            FROM verses 
            WHERE first_char = ? AND last_char = ?
            ORDER BY book, chapter, verse
            LIMIT 10
        """, (first_letter, last_letter))
        
        results = cursor.fetchall()
        conn.close()
        
        # Format results
        verses_found = []
        for row in results:
            verse_data = {
                "book": row["book"],
                "chapter": row["chapter"],
                "verse": row["verse"],
                "reference": f'{row["book"]} {row["chapter"]}:{row["verse"]}',
                "text": row["text_cleaned"] or row["text_raw"],  # Utiliser text_cleaned en priorité
                "first_char": row["first_char"],
                "last_char": row["last_char"]
            }
            
            # Ajouter la traduction seulement si elle existe et n'est pas vide
            if row["translation_fr"] and row["translation_fr"].strip():
                verse_data["translation_fr"] = row["translation_fr"]
            
            # Ajouter le commentaire de Rashi seulement s'il existe et n'est pas vide
            if row["commentary_rashi"] and row["commentary_rashi"].strip():
                verse_data["rashi_commentary"] = row["commentary_rashi"]
                
            verses_found.append(verse_data)
        
        return jsonify({
            "results": verses_found,
            "count": len(verses_found),
            "name_match": name_match,
            "search_type": "name_match"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tanakh_bp.route("/names", methods=["GET"])
@cross_origin()
def get_names():
    """Get all matched Hebrew names for autocomplete"""
    matched_names = load_matched_names()
    names = [name_info['french_name'] for name_info in matched_names]
    return jsonify({'names': names})

@tanakh_bp.route("/name/<name>", methods=["GET"])
@cross_origin()
def get_name_info(name):
    """Get information about a specific Hebrew name"""
    matched_names = load_matched_names()
    for name_info in matched_names:
        if name.lower() == name_info['french_name'].lower():
            return jsonify(name_info)
    return jsonify({'error': 'Name not found'}), 404

@tanakh_bp.route("/stats", methods=["GET"])
@cross_origin()
def get_stats():
    """Endpoint pour obtenir des statistiques sur la base de données."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Nombre total de versets
        cursor.execute("SELECT COUNT(*) as total FROM verses")
        total_verses = cursor.fetchone()["total"]
        
        # Nombre de livres
        cursor.execute("SELECT COUNT(DISTINCT book) as total_books FROM verses")
        total_books = cursor.fetchone()["total_books"]
        
        # Livres disponibles
        cursor.execute("SELECT DISTINCT book FROM verses ORDER BY book")
        books = [row["book"] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "total_verses": total_verses,
            "total_books": total_books,
            "books": books
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tanakh_bp.route("/test", methods=["GET"])
@cross_origin()
def test_endpoint():
    """Endpoint de test pour vérifier que l'API fonctionne."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test avec Psaumes 20:2
        cursor.execute("""
            SELECT book, chapter, verse, text_raw, text_cleaned, first_char, last_char
            FROM verses 
            WHERE book = 'Ps' AND chapter = 20 AND verse = 2
        """)
        
        psalm_20_2 = cursor.fetchone()
        conn.close()
        
        if psalm_20_2:
            return jsonify({
                "test": "success",
                "psalm_20_2": {
                    "book": psalm_20_2["book"],
                    "chapter": psalm_20_2["chapter"],
                    "verse": psalm_20_2["verse"],
                    "text_raw": psalm_20_2["text_raw"],
                    "text_cleaned": psalm_20_2["text_cleaned"],
                    "first_char": psalm_20_2["first_char"],
                    "last_char": psalm_20_2["last_char"]
                }
            })
        else:
            return jsonify({"test": "failed", "message": "Psalm 20:2 not found"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tanakh_bp.route("/letter_pair_occurrences", methods=["GET"])
@cross_origin()
def get_letter_pair_occurrences():
    """Endpoint pour obtenir les occurrences de paires de lettres."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT first_letter, last_letter, occurrence_count FROM letter_pair_occurrences ORDER BY occurrence_count DESC")
        results = cursor.fetchall()
        conn.close()
        
        occurrences = []
        for row in results:
            occurrences.append({
                "first_letter": row["first_letter"],
                "last_letter": row["last_letter"],
                "count": row["occurrence_count"]
            })
        
        return jsonify({"letter_pair_occurrences": occurrences}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

