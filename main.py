import sys
import os
import requests
from bs4 import BeautifulSoup
import string

def checkRarity(minimum_rarity):
    rarities = ["common", "rare", "epic", "legendary"]
    if minimum_rarity not in rarities:
        return False
    return True

def getCharacterTables(soup):
    characterTables = []

    tbodys = soup.find_all("tbody")
    for tbody in tbodys:
        firstRowAnchors = tbody.find("tr").find_all("a")
        for i in range(len(firstRowAnchors)):
            if firstRowAnchors[i].get_text() == "Skins":
                characterTables.append((firstRowAnchors[i - 1].get_text(), tbody))
                break
    
    return characterTables

def rarity1GreaterEqualRarity2(rarity1, rarity2):
    rarities = ["common", "rare", "epic", "legendary"]
    
    index1 = -1
    index2 = -1

    for i in range(len(rarities)):
        if rarities[i] in rarity1:
            index1 = i
        if rarities[i] in rarity2:
            index2 = i
    
    return index1 >= index2

def indexToLexicographic(index):
    c2 = chr(index % 26 + 97)
    c1 = chr(index // 26 + 97)

    return c1 + c2

def main(minimum_rarity, download_dir):
    # URL of the website to scrape
    URL = "https://overwatch.fandom.com/wiki/Heroes_skins"

    if not checkRarity(minimum_rarity):
        print("Invalid rarity [" + minimum_rarity + "], valid rarities: Common, Rare, Epic, Legendary")
        exit(-1)

    # Create the directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Send a GET request to fetch the HTML content
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        print("Failed to fetch HTML content")
        exit(-1)

    character_tables = getCharacterTables(soup)

    for character_name, character_table in character_tables:
        character_rows = character_table.find_all("tr")
        correct_rarity = False
        skin_index = 0
        for row in character_rows:
            correct_rarity = correct_rarity or rarity1GreaterEqualRarity2(row.get_text().lower(), minimum_rarity)
            if correct_rarity:
                skins = row.find_all("td")
                for skin in skins:
                    skin_name = skin.find("b")
                    if skin_name is None:
                        break
                    skin_name = skin_name.get_text().strip()
                    skin_image_url = skin.find("a")["href"]
                    img_filename = f"{character_name}_{str(indexToLexicographic(skin_index))}_{skin_name}.png"
                    img_path = os.path.join(download_dir, img_filename)
                    try:
                        img_response = requests.get(skin_image_url)
                    except:
                        print(f"Failed to download {character_name}, {img_filename}")
                    with open(img_path, "wb") as img_file:
                        img_file.write(img_response.content)
                    skin_index += 1

if (__name__ == "__main__"):
    if len(sys.argv) < 2:
        print("Usage: python main.py <minimum rarity>")
        print("valid rarities: Common, Rare, Epic, Legendary")
        exit(-1)
    elif len(sys.argv) == 2:
        print("Download directory missing, use default directory? [Y for yes]")
        response = input()
        if response.lower() == 'y':
            if hasattr(sys, 'frozen'):
                basis = sys.executable
            else:
                basis = sys.argv[0]
            download_dir = os.path.join(os.path.dirname(basis), "all_skins")
        else:
            exit(-1)
    else:
        download_dir = sys.argv[2]
    main(sys.argv[1].lower(), download_dir)