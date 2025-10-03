import re
import json

def extract_names_from_finejudaica(page_content):
    names = []
    # Regex to find patterns like "AALIYAH (**עליה**): Hebrew name meaning..."
    # It captures the French transliteration and the Hebrew script.
    pattern = re.compile(r'([A-Z]+(?:\'[A-Z]+)?)\s+\(\*\*([\u0590-\u05FF]+)\*\*\):\s+Hebrew name meaning "([^"]+)"')
    
    for line in page_content.splitlines():
        match = pattern.search(line)
        if match:
            french_name = match.group(1).strip()
            hebrew_script = match.group(2).strip()
            meaning = match.group(3).strip()
            names.append({
                'french': french_name,
                'hebrew': hebrew_script,
                'meaning': meaning
            })
    return names

if __name__ == '__main__':
    # For now, we will manually paste the content of the Fine Judaica page here.
    # In a real scenario, we would use a browser tool to get the content.
    # I will use the content from the last browser_view call.
    page_content = """
AALIYAH (**עליה**): Variant spelling of Hebrew Aliya, meaning "to ascend, to go up."

ABIGAYIL (**אביגיל**): Hebrew name meaning "father rejoices." In the bible, this is the name of the wife of King David. Also spelled Avigayil.

ALIYA (**עליה**): Hebrew name meaning "to ascend, to go up." Compare with another form of Aliya.

ALIYAH (**עליה**): Variant spelling of Hebrew Aliya, meaning "to ascend, to go up." Compare with another form of Aliyah.

ALIZA (**עליזה**): Variant spelling of both Hebrew Aleeza and Alitza, meaning "joy." 

ALITZA (**עליצה**): Hebrew name meaning "joy."

ALMA (**עלמה**): Hebrew name meaning "maiden." Compare with another form of Alma.

ALMAH: Variant spelling of Hebrew Alma, meaning "maiden." Compare with another form of Almah.

ALONA (**אלוּנה**): Feminine form of Hebrew Alon, meaning "oak tree."

ALYA (**אליה**): Aramaic and Hebrew name meaning "dirge, elegy" or "sheep's tail." In astronomy, this is the traditional name for Theta Serpentis, a star in the constellation Serpens. 

AMALYA (**עמליה**): Hebrew name meaning "industrious" or "work of the Lord." 

AMINA (**אמינה**): Hebrew name meaning "faithful, trusted." Compare with another form of Amina.

AMINE: Variant spelling of Hebrew Amina, meaning "faithful, trusted."

AMINTA (**אמינתה**): Hebrew name meaning "truth, friendship." Compare with another form of Aminta.

AMINTAH: Variant spelling of Hebrew Aminta, meaning "defender."

AMIRA (**אמירה**): Hebrew name meaning "speech, utterance." Compare with another form of Amira.

AMIT (**עמית**): Hebrew unisex name meaning "friend."

AMITA (**אמתה**): Hebrew name meaning "honest, upright." Compare with another form of Amita.

ANAT (**ענת**): Unisex form of Hebrew Anath, meaning "answer (to prayer)." Compare with another form of Anat.

APHRA (**רפע**): Hebrew unisex name derived from the word aphra, meaning "ashes, dust" and "clay, loam." In the bible, this is part of the name of a Philistine city, Bethel-aphrah.

APHRODIT (**אפרוֹדית**): Hebrew form of Greek Aphrodite, meaning "risen from the foam."

ARI'EL (**אריאל**): Hebrew unisex name meaning "lion of god." In the bible, this is a name applied to the city of Jerusalem, and the name of a chief of the returning exiles. In the Apocrypha, this is the name of an archangel who rules the waters. It is also the name of a moon of Uranus, and the name of a spirit in Shakespeare's play "The Tempest."

ASHERAH (**אשרה**): Hebrew name meaning "groves (for idol worship)" or "blessed, fortunate." In the bible, this is the Hebrew name for the Babylonian-Canaanite goddess Astarte. It is also the name for her images and sacred trees or poles used for worshiping her. 

ASHERDU: Hittite form of Hebrew Asherah, perhaps having the same meaning "groves (for idol worship)" or "blessed, fortunate."

ASHTAROWTH (**עשתרוֹת**): Hebrew name, meaning "star." In the bible, this is the name applied to false goddesses in the Canaanite religion, usually related to a fertility cult. It is also the name of a city in Bashan east of the Jordan given to Manasseh.

ASHTORETH (**עשתרת**): Hebrew name meaning "star." In the bible, this is the name of the principal female deity of the Semitic nations, worshiped in war and fertility. Equated with Assyrian Ishtar and Greek Astarte. 

ATARA: Variant spelling of Hebrew Atarah, meaning" crown" or "wreath."

ATARAH (**עטרה**): Hebrew name meaning "crown" or "wreath." In the bible, this is the name of the wife of Jerahmeel. 

AVAGAIL: Variant spelling of Hebrew Avigayil, meaning "father rejoices."

AVI (**אבי**): Variant spelling of Hebrew Abiy, meaning "my father." Compare with masculine Avi.

AVICHAYIL (**אביחיל**): Variant spelling of Hebrew unisex Abihayil, meaning "father of might." 

AVIGAIL: Variant spelling of Hebrew Avigayil, meaning "father rejoices."

AVIGAL (**אביגל**): Unisex form of Hebrew Avigayil, meaning "father rejoices."

AVIGAYIL (**אביגיל**): Variant spelling of Hebrew Abigayil, meaning "father rejoices." In the bible, this is the name of the wife of King David. 

AVISHAG (**אבישג**): Variant spelling of Hebrew Abiyshag, meaning "my father is a wanderer" or "father of error." In the bible, this is the name of a young girl who cared for David in his old age. 

AVIVA (**אביבה**): Feminine form of Hebrew Aviv, meaning "springtime."

AVIYAH (**אביה**): Variant spelling of Hebrew unisex Abiyah, meaning "Yahweh is my father." 

AVRA: Short form of Hebrew Avrahamit, meaning "father of a multitude." Also spelled Abra.

AVRAHAMIT (**אברהמית**): Feminine form of Hebrew Avraham, meaning "father of a multitude." Also spelled Abrahamit.

AYA (**איה**): Variant spelling of Hebrew unis...41874 bytes truncated..."""

    extracted_names = extract_names_from_finejudaica(page_content)

    with open('hebrew_names_finejudaica.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_names, f, ensure_ascii=False, indent=4)

    print(f"Extracted {len(extracted_names)} names from Fine Judaica and saved to hebrew_names_finejudaica.json")


