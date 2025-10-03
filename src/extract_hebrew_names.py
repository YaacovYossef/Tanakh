import re
import json

def extract_names_from_markdown_content(markdown_content):
    names = []
    for line in markdown_content.splitlines():
        match = re.match(r'^\d+\.\s*([A-Za-zÀ-ÿ\s-]+?)(?:\s*\(([^)]+)\))?$', line.strip())
        if match:
            name_fr = match.group(1).strip()
            name_he = match.group(2).strip() if match.group(2) else ''
            # Keep the hebrew name as is, even if it contains Latin characters, for now.
            # We will filter for actual Hebrew characters later in the matching script.
            names.append({
                'french': name_fr,
                'hebrew': name_he
            })
    return names

if __name__ == '__main__':
    all_hebrew_names = []

    # Boys' names
    with open('boys_names.md', 'r', encoding='utf-8') as f:
        boys_markdown_content = f.read()
    boys_names = extract_names_from_markdown_content(boys_markdown_content)
    all_hebrew_names.extend(boys_names)

    # Girls' names
    with open('girls_names.md', 'r', encoding='utf-8') as f:
        girls_markdown_content = f.read()
    girls_names = extract_names_from_markdown_content(girls_markdown_content)
    all_hebrew_names.extend(girls_names)

    with open('hebrew_names_integraliah.json', 'w', encoding='utf-8') as f:
        json.dump(all_hebrew_names, f, ensure_ascii=False, indent=4)

    print(f"Extracted {len(all_hebrew_names)} names from Integraliah and saved to hebrew_names_integraliah.json")


