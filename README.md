# Application de Recherche dans le Tanakh - Couples de Lettres et Prénoms Hébreux

## Description

Cette application permet de rechercher des versets du Tanakh en utilisant des couples de lettres hébraïques, avec une fonctionnalité spéciale pour associer des prénoms hébreux à leurs couples de lettres correspondants.

## Fonctionnalités

### ✨ Recherche par Prénom Hébreu
- Saisie d'un prénom hébreu avec autocomplétion
- Affichage automatique du prénom en caractères hébreux
- Identification du couple de lettres (première et dernière lettre)
- Recherche des versets correspondants dans le Tanakh

### 🔤 Recherche par Couples de Lettres
- Saisie directe de la première et dernière lettre hébraïque
- Recherche dans l'intégralité du Tanakh
- Affichage du nombre d'occurrences

### 📖 Présentation des Résultats
- Interface moderne et attrayante avec design en dégradé
- Cartes de versets avec mise en forme élégante
- Texte hébreu avec direction RTL correcte
- Traduction française du Rabbinat incluse
- Commentaires de Rashi (quand disponibles)
- Mise en évidence des lettres correspondantes

## Structure du Projet

```
tanakh-search-app/
├── src/
│   ├── main.py                          # Application Flask principale
│   ├── routes/
│   │   └── tanakh.py                    # Routes API pour les recherches
│   ├── static/
│   │   ├── index.html                   # Interface utilisateur
│   │   ├── styles.css                   # Styles CSS modernes
│   │   └── script.js                    # JavaScript interactif
│   ├── tanakh.db                        # Base de données SQLite du Tanakh
│   ├── letter_pair_occurrences.json    # Données des occurrences de couples de lettres
│   ├── matched_names.json              # Correspondances prénoms-couples de lettres
│   ├── hebrew_names_finejudaica.json   # Base de données des prénoms hébreux
│   └── extract_hebrew_names_finejudaica.py # Script d'extraction des prénoms
└── README.md                            # Documentation du projet
```

## Installation et Utilisation

### Prérequis
- Python 3.7+
- Flask
- SQLite3

### Installation
```bash
cd tanakh-search-app/src
pip install flask flask-cors
```

### Lancement de l'application
```bash
python3 main.py
```

L'application sera accessible à l'adresse : `http://localhost:5000`

## API Endpoints

### `/api/tanakh/search_by_name` (POST)
Recherche par prénom hébreu
```json
{
  "name": "ABIGAYIL"
}
```

### `/api/tanakh/search` (POST)
Recherche par couple de lettres
```json
{
  "start_letter": "א",
  "end_letter": "ל"
}
```

### `/api/tanakh/names` (GET)
Récupère la liste des prénoms hébreux disponibles

## Base de Données

### Prénoms Hébreux Supportés
L'application inclut actuellement 12 prénoms hébreux avec leurs caractères hébreux authentiques :
- ABIGAYIL (אביגיל) - "father rejoices"
- ALIYA (עליה) - "to ascend, to go up"
- ALITZA (עליצה) - "joy"
- ALMA (עלמה) - "maiden"
- AMALYA (עמליה) - "industrious"
- AMINA (אמינה) - "faithful, trusted"
- AMINTA (אמינתה) - "truth, friendship"
- AMIRA (אמירה) - "speech, utterance"
- AMITA (אמתה) - "honest, upright"
- ASHERAH (אשרה) - "groves (for idol worship)"
- ASHTORETH (עשתרת) - "star"
- ATARAH (עטרה) - "crown"

### Contenu du Tanakh
- Texte hébreu complet
- Traductions françaises du Rabbinat
- Commentaires de Rashi
- Indexation par couples de lettres

## Caractéristiques Techniques

### Frontend
- Interface responsive avec CSS Grid et Flexbox
- JavaScript moderne avec gestion d'événements
- Autocomplétion pour les prénoms
- Navigation par onglets
- États de chargement et gestion d'erreurs

### Backend
- API REST avec Flask
- Base de données SQLite optimisée
- Gestion CORS pour les requêtes cross-origin
- Algorithme de correspondance efficace

### Design
- Palette de couleurs moderne (dégradé violet)
- Typographie adaptée au texte hébreu
- Cartes de versets avec effets de survol
- Interface intuitive et accessible

## Version Gratuite

Cette version gratuite offre :
- ✅ Recherche complète dans le Tanakh
- ✅ 12 prénoms hébreux pré-configurés
- ✅ Présentation attrayante des résultats
- ✅ Traductions et commentaires inclus
- ✅ Interface moderne et responsive

## Développement Futur

### Améliorations Possibles
- Extension de la base de données de prénoms hébreux
- Ajout de fonctionnalités musicales
- Support de prénoms personnalisés
- Recherche avancée avec filtres
- Export des résultats

### Extensibilité
Le système est conçu pour être facilement extensible :
- Ajout de nouveaux prénoms via JSON
- Intégration de nouvelles sources de données
- Personnalisation de l'interface
- Ajout de nouvelles langues de traduction

## Licence

Ce projet est développé pour un usage éducatif et spirituel, respectant les sources traditionnelles du Tanakh.

