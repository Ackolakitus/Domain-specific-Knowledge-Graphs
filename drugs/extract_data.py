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
                kingdoms.add(classification.find('drugbank:kingdom', ns).text.title())

            if classification.find('drugbank:superclass', ns) is not None:
                superclasses.add(classification.find('drugbank:superclass', ns).text)

            if classification.find('drugbank:class', ns) is not None:
                classes.add(classification.find('drugbank:class', ns).text)

            if classification.find('drugbank:subclass', ns) is not None:
                subclasses.add(classification.find('drugbank:subclass', ns).text)

            if classification.find('drugbank:direct-parent', ns) is not None:
                parents.add(classification.find('drugbank:direct-parent', ns).text)

        drug_info = {
            'drugbank-id': drug.find('drugbank:drugbank-id', ns).text,
            'type': drug.attrib.get('type'),
            'name': drug.find('drugbank:name', ns).text if drug.find('drugbank:name', ns) is not None else None,
            'state': drug.find('drugbank:state', ns).text if drug.find('drugbank:state', ns) is not None else None,
            'groups': [group.text for group in drug.findall('drugbank:groups/drugbank:group', ns)],
            'salts': [{'drugbank-id': salt.find('drugbank:drugbank-id', ns).text,
                       'name': salt.find('drugbank:name', ns).text}
                      for salt in drug.findall('drugbank:salts/drugbank:salt', ns)],
            'classification': {
                'kingdom': classification.find('drugbank:kingdom',
                                               ns).text.title() if classification is not None else None,
                'superclass': classification.find('drugbank:superclass',
                                                  ns).text if classification is not None else None,
                'class': classification.find('drugbank:class', ns).text if classification is not None else None,
                'subclass': classification.find('drugbank:subclass', ns).text if classification is not None else None,
                'parent': classification.find('drugbank:direct-parent',
                                              ns).text if classification is not None else None,
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
            # 'pathways': [{'name': pathway.find('drugbank:name', ns).text,
            #               'smpdb-id': pathway.find('drugbank:smpdb-id', ns).text,
            #               'category': pathway.find('drugbank:category', ns).text}
            #              for pathway in drug.findall('drugbank:pathways/drugbank:pathway', ns)],
        }

        if type == 'biotech':
            biotech_info.append(drug_info)
        elif type == 'small molecule':
            small_molecules_info.append(drug_info)

    return biotech_info, small_molecules_info, kingdoms, superclasses, classes, subclasses, parents


# Example usage
def create_data():
    file_path = './data/full database.xml'
    biotech_drugs, small_molecule_drugs, kingdoms, superclasses, classes, subclasses, parents = extract_drug_info(
        file_path)

    save_to_pickle(biotech_drugs, './data/extracted-biotech-drugs.pkl')
    save_to_json(biotech_drugs, './data/extracted-biotech-drugs.json')

    save_to_pickle(small_molecule_drugs, './data/small-molecule-drugs.pkl')
    save_to_json(small_molecule_drugs, './data/small-molecule-drugs.json')


def extract_classification_sets(drugs):
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


def print_data_items(data):
    for item in data:
        print(item)


def print_data_items_count(data):
    for item, count in data.items():
        print(f"{item}: {count} items")


def extract_classification_relationships(drugs):
    relationships_set = set()

    for drug in drugs:
        if drug.get('name', "") == "Ceftibuten":
            print("EVEGO BE")

        classification = drug.get('classification', {})
        if classification:
            if kingdom := classification.get('kingdom'):
                relationships_set.add(('Root', 'Kingdoms', 'Kingdom', kingdom))
            if superclass := classification.get('superclass'):
                relationships_set.add(('Kingdom', kingdom, 'Superclass', superclass))
            if class_ := classification.get('class'):
                relationships_set.add(('Superclass', superclass, 'Class', class_))
            if subclass := classification.get('subclass'):
                relationships_set.add(('Class', class_, 'Subclass', subclass))
            if direct_parent := classification.get('direct-parent'):
                for key, value in classification.items():
                    if key != "direct-parent" and value == direct_parent:
                        parent_type = key.title()
                        relationships_set.add((f'{parent_type}', direct_parent, 'Drug', drug.get('name')))
                        break

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
    # create_data()

    # data = load_from_json('./data/extracted-biotech-drugs.json')
    data = load_from_json('./data/small-molecule-drugs.json')

    # kingdoms, superclasses, classes, subclasses = extract_classification_sets(data)
    #
    # print("Kingdoms:")
    # print_data_items_count(kingdoms)
    #
    # print("\nSuperclasses:")
    # print_data_items_count(superclasses)
    #
    # print("\nClasses:")
    # print_data_items_count(classes)
    #
    # print("\nSubclasses:")
    # print_data_items_count(subclasses)

    # relations = extract_classification_relationships(data)
    # print_data_items(relations)
    # print_relations_neo4j(relations)

    # TOO MUCH
    # drug_interactions = extract_interaction_relationships(data, 'drug')
    # print_data_items(drug_interactions)
    # print(len(drug_interactions))

    food_interactions = extract_interaction_relationships(data, 'food')
    print_data_items(food_interactions)
    print(len(food_interactions))
if __name__ == '__main__':
    main()
