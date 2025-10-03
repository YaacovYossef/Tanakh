#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer les analyses des couples de lettres et des occurrences par lettre
- Graphique en camembert des couples de lettres les plus fréquents
- Analyse de répartition par lettres individuelles
- Visualisations des occurrences communes
"""

import sqlite3
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from collections import Counter, defaultdict
import seaborn as sns

# Configuration pour l'affichage des caractères hébreux
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Noto Sans']

def get_db_connection():
    """Obtient une connexion à la base de données SQLite."""
    return sqlite3.connect('tanakh.db')

def analyze_letter_pairs():
    """
    Analyse les couples de lettres dans la base de données
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer toutes les occurrences de couples de lettres
    cursor.execute("""
        SELECT first_letter, last_letter, occurrence_count 
        FROM letter_pair_occurrences 
        ORDER BY occurrence_count DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    # Préparer les données
    letter_pairs = []
    counts = []
    
    for first_letter, last_letter, count in results:
        pair = f"{first_letter}{last_letter}"
        letter_pairs.append(pair)
        counts.append(count)
    
    return letter_pairs, counts

def analyze_individual_letters():
    """
    Analyse la répartition des lettres individuelles
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Compter les occurrences de chaque lettre en première position
    cursor.execute("""
        SELECT first_letter, SUM(occurrence_count) as total_first
        FROM letter_pair_occurrences 
        GROUP BY first_letter
        ORDER BY total_first DESC
    """)
    first_letters = cursor.fetchall()
    
    # Compter les occurrences de chaque lettre en dernière position
    cursor.execute("""
        SELECT last_letter, SUM(occurrence_count) as total_last
        FROM letter_pair_occurrences 
        GROUP BY last_letter
        ORDER BY total_last DESC
    """)
    last_letters = cursor.fetchall()
    
    conn.close()
    
    return first_letters, last_letters

def create_pie_chart(letter_pairs, counts, top_n=15):
    """
    Crée un graphique en camembert des couples de lettres les plus fréquents
    """
    # Prendre les top_n couples les plus fréquents
    top_pairs = letter_pairs[:top_n]
    top_counts = counts[:top_n]
    
    # Calculer le pourcentage pour "Autres"
    total_count = sum(counts)
    top_total = sum(top_counts)
    others_count = total_count - top_total
    
    if others_count > 0:
        top_pairs.append('Autres')
        top_counts.append(others_count)
    
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Couleurs personnalisées
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_pairs)))
    
    # Créer le camembert
    wedges, texts, autotexts = ax.pie(
        top_counts, 
        labels=top_pairs,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 10}
    )
    
    # Améliorer l'apparence
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Distribution des Couples de Lettres les Plus Fréquents dans le Tanakh', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Ajouter une légende avec les comptes
    legend_labels = [f'{pair}: {count:,}' for pair, count in zip(top_pairs, top_counts)]
    ax.legend(wedges, legend_labels, title="Couples de lettres", 
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    plt.savefig('letter_pairs_pie_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return top_pairs, top_counts

def create_bar_chart_individual_letters(first_letters, last_letters):
    """
    Crée des graphiques en barres pour les lettres individuelles
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Graphique pour les premières lettres
    letters_first = [item[0] for item in first_letters[:15]]
    counts_first = [item[1] for item in first_letters[:15]]
    
    bars1 = ax1.bar(letters_first, counts_first, color='skyblue', alpha=0.8)
    ax1.set_title('Lettres les Plus Fréquentes en Première Position', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Lettres Hébraïques', fontsize=12)
    ax1.set_ylabel('Nombre d\'Occurrences', fontsize=12)
    ax1.tick_params(axis='x', rotation=0)
    
    # Ajouter les valeurs sur les barres
    for bar, count in zip(bars1, counts_first):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{count:,}', ha='center', va='bottom', fontsize=9)
    
    # Graphique pour les dernières lettres
    letters_last = [item[0] for item in last_letters[:15]]
    counts_last = [item[1] for item in last_letters[:15]]
    
    bars2 = ax2.bar(letters_last, counts_last, color='lightcoral', alpha=0.8)
    ax2.set_title('Lettres les Plus Fréquentes en Dernière Position', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Lettres Hébraïques', fontsize=12)
    ax2.set_ylabel('Nombre d\'Occurrences', fontsize=12)
    ax2.tick_params(axis='x', rotation=0)
    
    # Ajouter les valeurs sur les barres
    for bar, count in zip(bars2, counts_last):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{count:,}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('individual_letters_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_heatmap_analysis():
    """
    Crée une heatmap des couples de lettres
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer toutes les lettres hébraïques uniques
    cursor.execute("SELECT DISTINCT first_letter FROM letter_pair_occurrences ORDER BY first_letter")
    first_letters = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT last_letter FROM letter_pair_occurrences ORDER BY last_letter")
    last_letters = [row[0] for row in cursor.fetchall()]
    
    # Créer une matrice des occurrences
    matrix = np.zeros((len(first_letters), len(last_letters)))
    
    cursor.execute("SELECT first_letter, last_letter, occurrence_count FROM letter_pair_occurrences")
    for first_letter, last_letter, count in cursor.fetchall():
        i = first_letters.index(first_letter)
        j = last_letters.index(last_letter)
        matrix[i][j] = count
    
    conn.close()
    
    # Créer la heatmap
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Utiliser une échelle logarithmique pour mieux voir les variations
    matrix_log = np.log1p(matrix)  # log(1 + x) pour éviter log(0)
    
    sns.heatmap(matrix_log, 
                xticklabels=last_letters, 
                yticklabels=first_letters,
                cmap='YlOrRd',
                ax=ax,
                cbar_kws={'label': 'Log(Occurrences + 1)'})
    
    ax.set_title('Heatmap des Couples de Lettres dans le Tanakh\n(Échelle Logarithmique)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Dernière Lettre', fontsize=12)
    ax.set_ylabel('Première Lettre', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('letter_pairs_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_statistics_report():
    """
    Génère un rapport statistique détaillé
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Statistiques générales
    cursor.execute("SELECT COUNT(*) FROM letter_pair_occurrences")
    total_pairs = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(occurrence_count) FROM letter_pair_occurrences")
    total_occurrences = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(occurrence_count) FROM letter_pair_occurrences")
    avg_occurrences = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(occurrence_count), MIN(occurrence_count) FROM letter_pair_occurrences")
    max_occ, min_occ = cursor.fetchone()
    
    # Top 10 des couples
    cursor.execute("""
        SELECT first_letter, last_letter, occurrence_count 
        FROM letter_pair_occurrences 
        ORDER BY occurrence_count DESC 
        LIMIT 10
    """)
    top_10 = cursor.fetchall()
    
    conn.close()
    
    # Créer le rapport
    report = {
        'statistics': {
            'total_letter_pairs': total_pairs,
            'total_occurrences': total_occurrences,
            'average_occurrences': round(avg_occurrences, 2),
            'max_occurrences': max_occ,
            'min_occurrences': min_occ
        },
        'top_10_pairs': [
            {
                'pair': f"{first}{last}",
                'first_letter': first,
                'last_letter': last,
                'count': count,
                'percentage': round((count / total_occurrences) * 100, 2)
            }
            for first, last, count in top_10
        ]
    }
    
    # Sauvegarder le rapport
    with open('letter_pairs_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report

def main():
    """
    Fonction principale pour générer toutes les analyses
    """
    print("=== Génération des analyses des couples de lettres ===")
    
    # 1. Analyser les couples de lettres
    print("1. Analyse des couples de lettres...")
    letter_pairs, counts = analyze_letter_pairs()
    print(f"   - {len(letter_pairs)} couples de lettres analysés")
    
    # 2. Créer le graphique en camembert
    print("2. Création du graphique en camembert...")
    top_pairs, top_counts = create_pie_chart(letter_pairs, counts)
    print(f"   - Graphique sauvegardé: letter_pairs_pie_chart.png")
    
    # 3. Analyser les lettres individuelles
    print("3. Analyse des lettres individuelles...")
    first_letters, last_letters = analyze_individual_letters()
    create_bar_chart_individual_letters(first_letters, last_letters)
    print(f"   - Graphique sauvegardé: individual_letters_analysis.png")
    
    # 4. Créer la heatmap
    print("4. Création de la heatmap...")
    create_heatmap_analysis()
    print(f"   - Heatmap sauvegardée: letter_pairs_heatmap.png")
    
    # 5. Générer le rapport statistique
    print("5. Génération du rapport statistique...")
    report = generate_statistics_report()
    print(f"   - Rapport sauvegardé: letter_pairs_analysis_report.json")
    
    # Afficher un résumé
    print("\n=== Résumé des analyses ===")
    print(f"Nombre total de couples de lettres: {report['statistics']['total_letter_pairs']}")
    print(f"Nombre total d'occurrences: {report['statistics']['total_occurrences']:,}")
    print(f"Moyenne d'occurrences par couple: {report['statistics']['average_occurrences']}")
    print(f"Couple le plus fréquent: {report['top_10_pairs'][0]['pair']} ({report['top_10_pairs'][0]['count']:,} occurrences)")
    
    print("\nTop 5 des couples de lettres:")
    for i, pair_info in enumerate(report['top_10_pairs'][:5], 1):
        print(f"  {i}. {pair_info['pair']}: {pair_info['count']:,} occurrences ({pair_info['percentage']}%)")

if __name__ == "__main__":
    main()

