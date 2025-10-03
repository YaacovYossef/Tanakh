import json
import re

def match_names_to_letter_pairs(letter_pairs_data, hebrew_names_data):
    matched_names = []
    # Create a dictionary for quick lookup of letter pair occurrences
    letter_pair_map = {}
    for pair_entry in letter_pairs_data["letter_pair_occurrences"]:
        key = (pair_entry["first_letter"], pair_entry["last_letter"])
        letter_pair_map[key] = pair_entry["count"]

    for name_info in hebrew_names_data:
        hebrew_name_from_data = name_info.get("hebrew")
        french_name = name_info.get("french")

        if hebrew_name_from_data and re.search(r'[\u0590-\u05FF]', hebrew_name_from_data):
            cleaned_hebrew_name = "".join(filter(lambda x: u'\u05d0' <= x <= u'\u05ea', hebrew_name_from_data))
            if len(cleaned_hebrew_name) >= 2:
                first_letter = cleaned_hebrew_name[0]
                last_letter = cleaned_hebrew_name[-1]
                
                pair_key = (first_letter, last_letter)
                if pair_key in letter_pair_map:
                    matched_names.append({
                        "french_name": french_name,
                        "hebrew_name": hebrew_name_from_data,
                        "letter_pair": f"{first_letter}{last_letter}",
                        "occurrences": letter_pair_map[pair_key]
                    })
    return matched_names

if __name__ == '__main__':
    # Load letter pair occurrences
    with open('letter_pair_occurrences.json', 'r', encoding='utf-8') as f:
        letter_pair_data = json.load(f)

    # Load Hebrew names from Fine Judaica
    with open('hebrew_names_finejudaica.json', 'r', encoding='utf-8') as f:
        hebrew_names_data = json.load(f)

    # Match names to letter pairs
    matched_results = match_names_to_letter_pairs(letter_pair_data, hebrew_names_data)

    # Save the matched results to a new JSON file
    with open('matched_names.json', 'w', encoding='utf-8') as f:
        json.dump(matched_results, f, ensure_ascii=False, indent=4)

    print(f"Matched {len(matched_results)} names and saved to matched_names.json")


