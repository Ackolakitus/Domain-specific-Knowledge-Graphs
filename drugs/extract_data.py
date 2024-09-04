import sys
import xml.etree.ElementTree as ET
import pickle
import json
from collections import defaultdict


def save_to_pickle(data, file_path):
    with open(file_path, 'wb') as pickle_file:
        pickle.dump(data, pickle_file)


def load_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data


def save_to_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def load_from_pickle(file_path):
    with open(file_path, 'rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data


def extract_drug_info(file_path):
    ns = {'drugbank': 'http://www.drugbank.ca'}

    tree = ET.parse(file_path)
    root = tree.getroot()

    kingdoms = set()
    superclasses = set()
    classes = set()
    subclasses = set()
    parents = set()

    biotech_info = []
    small_molecules_info = []

    for drug in root.findall('drugbank:drug', ns):
        type = drug.attrib.get('type')
        classification = drug.find('drugbank:classification', ns)

        if classification is not None:
            # Add to respective sets
            if classification.find('drugbank:kingdom', ns) is not None:
                kingdoms.add(str(classification.find('drugbank:kingdom', ns).text).lower().title())

            if classification.find('drugbank:superclass', ns) is not None:
                superclasses.add(str(classification.find('drugbank:superclass', ns).text).lower().capitalize())

            if classification.find('drugbank:class', ns) is not None:
                classes.add(str(classification.find('drugbank:class', ns).text).lower().capitalize())

            if classification.find('drugbank:subclass', ns) is not None:
                subclasses.add(str(classification.find('drugbank:subclass', ns).text).lower().capitalize())

            if classification.find('drugbank:direct-parent', ns) is not None:
                parents.add(str(classification.find('drugbank:direct-parent', ns).text).lower().capitalize())

        drug_info = {
            'drugbank-id': drug.find('drugbank:drugbank-id', ns).text,
            'type': drug.attrib.get('type'),
            'name': drug.find('drugbank:name', ns).text.lower().capitalize() if drug.find('drugbank:name', ns) is not None else None,
            'state': drug.find('drugbank:state', ns).text if drug.find('drugbank:state', ns) is not None else None,
            'groups': [group.text for group in drug.findall('drugbank:groups/drugbank:group', ns)],
            'salts': [salt.find('drugbank:name', ns).text for salt in drug.findall('drugbank:salts/drugbank:salt', ns)],
            'classification': {
                'kingdom': str(classification.find('drugbank:kingdom',
                                               ns).text).title() if classification is not None else None,
                'superclass': str(classification.find('drugbank:superclass',
                                                  ns).text).lower().capitalize() if classification is not None else None,
                'class': str(classification.find('drugbank:class', ns).text).lower().capitalize() if classification is not None else None,
                'subclass': str(classification.find('drugbank:subclass', ns).text).lower().capitalize() if classification is not None else None,
                'parent': str(classification.find('drugbank:direct-parent',
                                              ns).text).lower().capitalize() if classification is not None else None,
            } if classification is not None else None,
            'affected_organisms': [organism.text for organism in
                                   drug.findall('drugbank:affected-organisms/drugbank:affected-organism', ns)],
            'food_interactions': [interaction.text for interaction in
                                  drug.findall('drugbank:food-interactions/drugbank:food-interaction', ns)],
            'drug_interactions': [{'name': interaction.find('drugbank:name', ns).text,
                                   'description': interaction.find('drugbank:description', ns).text}
                                  for interaction in
                                  drug.findall('drugbank:drug-interactions/drugbank:drug-interaction', ns)],
            'external_links': drug.find('drugbank:external-link', ns).text if drug.find('drugbank:external-link',
                                                                                        ns) is not None else None,
        }

        if type == 'biotech':
            biotech_info.append(drug_info)
        elif type == 'small molecule':
            small_molecules_info.append(drug_info)

    return biotech_info, small_molecules_info, kingdoms, superclasses, classes, subclasses, parents


def save_data(biotech_drugs, small_molecule_drugs):
    save_to_pickle(biotech_drugs, './data/extracted-biotech-drugs.pkl')
    save_to_json(biotech_drugs, './data/extracted-biotech-drugs.json')

    save_to_pickle(small_molecule_drugs, './data/small-molecule-drugs.pkl')
    save_to_json(small_molecule_drugs, './data/small-molecule-drugs.json')


def extract_classification_sets_with_number_of_items(drugs):
    kingdoms = defaultdict(int)
    superclasses = defaultdict(int)
    classes = defaultdict(int)
    subclasses = defaultdict(int)

    for drug in drugs:
        classification = drug.get('classification', {})
        if classification:
            if kingdom := classification.get('kingdom'):
                kingdoms[kingdom] += 1
            if superclass := classification.get('superclass'):
                superclasses[superclass] += 1
            if class_ := classification.get('class'):
                classes[class_] += 1
            if subclass := classification.get('subclass'):
                subclasses[subclass] += 1

    return kingdoms, superclasses, classes, subclasses

def extract_classification_sets(drugs):
    kingdoms = set()
    superclasses = set()
    classes = set()
    subclasses = set()
    parents = set()

    for drug in drugs:
        classification = drug.get('classification', {})
        if classification:
            if (kingdom := classification.get('kingdom')) != 'None':
                kingdoms.add(kingdom.lower())
            if (superclass := classification.get('superclass')) != 'None':
                superclasses.add(superclass.lower())
            if (class_ := classification.get('class')) != 'None':
                classes.add(class_.lower())
            if (subclass := classification.get('subclass')) != 'None':
                subclasses.add(subclass.lower())
            if (parent := classification.get('parent')) != 'None':
                parents.add(parent.lower())

    return kingdoms, superclasses, classes, subclasses, parents.difference(kingdoms, superclasses, classes, subclasses)

def print_data_items(data):
    for item in data:
        print(item)


def print_data_items_count(data):
    for item, count in data.items():
        print(f"{item}: {count} items")


def extract_classification_relationships(drugs):
    relationships_set = set()

    for drug in drugs:
        last_classification_type = None
        last_classification_value = None

        classification = drug.get('classification', {})

        if classification:
            if (kingdom := classification.get('kingdom')) != 'None':
                relationships_set.add(('Root', 'Kingdoms', 'Kingdom', kingdom))
                last_classification_type = 'Kingdom'
                last_classification_value = kingdom

            if (superclass := classification.get('superclass')) != 'None':
                relationships_set.add(('Kingdom', kingdom, 'Superclass', superclass))
                last_classification_type = 'Superclass'
                last_classification_value = superclass

            if (class_ := classification.get('class')) != 'None':
                relationships_set.add(('Superclass', superclass, 'Class', class_))
                last_classification_type = 'Class'
                last_classification_value = class_

            if (subclass := classification.get('subclass')) != 'None':
                relationships_set.add(('Class', class_, 'Subclass', subclass))
                last_classification_type = 'Subclass'
                last_classification_value = subclass

            if (direct_parent := classification.get('parent')) != 'None':
                if any(key != "parent" and value.lower() == direct_parent.lower() for key, value in classification.items()):
                    relationships_set.add((last_classification_type, last_classification_value, 'Drug', drug.get('name')))
                else:
                    relationships_set.add((last_classification_type, last_classification_value, 'Parent', direct_parent))
                    relationships_set.add(('Parent', direct_parent, 'Drug', drug.get('name')))
            else:
                relationships_set.add((last_classification_type, last_classification_value, 'Drug', drug.get('name')))
        else:
            relationships_set.add(('Unclassified','Unclassified', 'Drug', drug.get('name')))

    relationships_set.add(('Root', 'Kingdoms', 'Unclassified', 'Unclassified'))
    return relationships_set


def print_relations_neo4j(data):
    for item in data:
        print(f'MATCH (a:{item[0]} {{name: {item[1]}}}), (b:{item[2]} {{name: {item[3]}}})')
        print(f'MERGE (a)-[:HAS_{str(item[2]).upper()}]->(b)')

def extract_interaction_relationships(drugs, type):
    relationships = []

    if type not in ['drug', 'food']:
        print("Invalid interactions type.")
        sys.exit(1)

    for drug in drugs:
        interactions = drug.get(f'{type}_interactions', {})

        drug_name = drug.get('name', "")

        for i in interactions:
            if type == 'drug':
                relationships.append((drug_name, i.get('name', ""), i.get('description', "")))
            elif type == 'food':
                relationships.append((drug_name, i))

    return relationships

def main():
    # ======== CREATE DATA =========
    # file_path = './data/full database.xml'
    # biotech_drugs, small_molecule_drugs, kingdoms, superclasses, classes, subclasses, parents = extract_drug_info(
    #     file_path)
    # save_data(biotech_drugs, small_molecule_drugs)

    # ======== LOAD DATA =========
    biotech = load_from_pickle('./data/extracted-biotech-drugs.pkl')
    small = load_from_pickle('./data/small-molecule-drugs.pkl')

    data = biotech + small

    kingdoms, superclasses, classes, subclasses, parents = extract_classification_sets(data)

    print(len(data)+len(kingdoms)+len(superclasses)+len(classes)+len(subclasses)+len(parents) + 2)

    relations = extract_classification_relationships(data)
    print(len(relations))

    # print_data_items(relations)
    # print_relations_neo4j(relations)

    # TOO MUCH
    # drug_interactions = extract_interaction_relationships(data, 'drug')
    # print_data_items(drug_interactions)
    # print(len(drug_interactions))

    # food_interactions = extract_interaction_relationships(data, 'food')
    # print_data_items(food_interactions)
    # print(len(food_interactions))
if __name__ == '__main__':
    main()
