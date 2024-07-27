import csv
import os
import re
import sys

import requests
from bs4 import BeautifulSoup


def extractPlantName(plant_name):
    match = re.match(r'^.*?(?=\s[A-Z]| \()', plant_name)
    if match:
        return match.group(0).strip()
    return plant_name


def extractPlantAuthors(s):
    capitals = [match.start() for match in re.finditer(r'[A-Z]', s)]
    parenthesis_index = s.find('(')

    if len(capitals) >= 2:
        second_capital_index = capitals[1]
    else:
        second_capital_index = len(s)  # Set to end if less than 2 capitals

    start_index = min(second_capital_index, parenthesis_index if parenthesis_index != -1 else len(s))

    return s[start_index:] if len(s[start_index:]) > 2 else ""


def getPlantFamily(plant_name):
    url = f"https://en.wikipedia.org/wiki/{plant_name}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    tds = soup.find_all("td")
    for td in tds:
        if "Family:" in td.text:
            next_td = td.find_next_sibling("td")

            if next_td:
                link = next_td.find("a")
                if link:
                    return link.text
    else:
        return ""


def getRowsPreprocessedDataset(file):
    file_extension = os.path.splitext(file)[1]

    if file_extension in ['.txt', '.csv']:
        with open(file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)

            fieldnames = next(reader)
            reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',')
            rows = list(reader)

            if 'Family' not in fieldnames:
                print("Error: 'Family' column not found in the CSV.")
                return

            symbol_to_family = {}

            for row in rows:
                row['Scientific Name with Author'] = row['Scientific Name with Author'].replace('×', '')
                symbol = row['Symbol']
                if symbol not in symbol_to_family:
                    symbol_to_family[symbol] = row['Family']

                if not symbol_to_family[symbol]:
                    plantName = extractPlantName(row['Scientific Name with Author'])
                    family = getPlantFamily(plantName)
                    symbol_to_family[symbol] = family

                if not row['Family']:
                    row['Family'] = symbol_to_family.get(row['Symbol'], '')

        return rows
    else:
        print(f"File is not of type csv/txt.")
        sys.exit(1)


def getDataFromRows(rows):

    families = set()
    relationships_set = set()
    symbol_to_data = {}
    scientific_name_to_symbol = {}
    symbols_to_remove = set()

    # Process rows and collect initial data
    for row in rows:
        symbol = row['Symbol']
        family = row['Family']
        name_with_author = row['Scientific Name with Author']
        common_name = row['Common Name']
        scientific_name = extractPlantName(name_with_author)
        authors = extractPlantAuthors(name_with_author)

        families.add(family)
        if symbol not in symbol_to_data:
            # First occurrence of the symbol
            symbol_to_data[symbol] = {
                'scientific_name': scientific_name,
                'common_name': common_name,
                'other_names': [],
                'authors': [],
                'symbol': symbol
            }
            if authors:
                symbol_to_data[symbol]['authors'].append(authors)
            # Create a relationship for the first occurrence
            relationships_set.add((scientific_name, family))
            # Map scientific name to the symbol
            scientific_name_to_symbol[scientific_name] = symbol
        else:
            # Subsequent occurrences of the symbol
            symbol_to_data[symbol]['other_names'].append(scientific_name)
            if authors:
                symbol_to_data[symbol]['authors'].append(authors)

    # Merge data for symbols with the same scientific name
    merged_data = {}
    for symbol, data in symbol_to_data.items():
        scientific_name = data['scientific_name']
        if scientific_name in scientific_name_to_symbol:
            primary_symbol = scientific_name_to_symbol[scientific_name]
            if primary_symbol != symbol:
                # Extend the primary symbol's data with the current symbol's data
                if primary_symbol not in merged_data:
                    merged_data[primary_symbol] = {
                        'scientific_name': data['scientific_name'],
                        'common_name': data['common_name'],
                        'other_names': [],
                        'authors': [],
                        'symbol': data['symbol']
                    }
                primary_data = merged_data[primary_symbol]
                primary_data['other_names'].extend(data['other_names'])
                primary_data['authors'].extend(data['authors'])
                primary_data['symbol'] = data['symbol']
                # Mark the current symbol for removal
                symbols_to_remove.add(symbol)
                continue
        merged_data[symbol] = data

    plants = [
        {
            'scientific_name': data['scientific_name'],
            'common_name': data['common_name'],
            'other_names': list(set(data['other_names'])),
            'authors': list(set(data['authors'])),
            'symbol': data['symbol']
        }
        for symbol, data in merged_data.items()
        if symbol not in symbols_to_remove
    ]

    relationships = [
        {'scientific_name': sn, 'family_name': fn}
        for sn, fn in relationships_set
    ]

    return plants, families, relationships



# Example usage
# rows = getRowsPreprocessedDataset('your_file.csv')
# plants, families, relationships = getDataFromRows(rows)

