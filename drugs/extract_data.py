import xml.etree.ElementTree as ET
import pickle
import json


def save_to_pickle(data, file_path):
    with open(file_path, 'wb') as pickle_file:
        pickle.dump(data, pickle_file)

def load_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def load_from_pickle(file_path):
    with open(file_path, 'rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data

def save_to_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def extract_drug_info(file_path):
    # Define the namespace
    ns = {'drugbank': 'http://www.drugbank.ca'}

    tree = ET.parse(file_path)
    root = tree.getroot()

    kingdoms = set()
    superclasses = set()
    classes = set()
    drugs_info = []

    for drug in root.findall('drugbank:drug', ns):

        classification = drug.find('drugbank:classification', ns)

        if classification is not None:
            # Add to respective sets
            if classification.find('drugbank:kingdom', ns) is not None:
                kingdoms.add(classification.find('drugbank:kingdom', ns).text)

            if classification.find('drugbank:superclass', ns) is not None:
                superclasses.add(classification.find('drugbank:superclass', ns).text)

            if classification.find('drugbank:class', ns) is not None:
                classes.add(classification.find('drugbank:class', ns).text)

        drug_info = {
            'type': drug.attrib.get('type'),
            'name': drug.find('drugbank:name', ns).text if drug.find('drugbank:name', ns) is not None else None,
            'state': drug.find('drugbank:state', ns).text if drug.find('drugbank:state', ns) is not None else None,
            'classification': {
                'direct-parent': classification.find('drugbank:direct-parent',
                                                     ns).text if classification is not None else None,
                'kingdom': classification.find('drugbank:kingdom', ns).text if classification is not None else None,
                'superclass': classification.find('drugbank:superclass',
                                                  ns).text if classification is not None else None,
                'class': classification.find('drugbank:class', ns).text if classification is not None else None,
                'subclass': classification.find('drugbank:subclass', ns).text if classification is not None else None,
            } if classification is not None else None,
            'synonyms': [syn.text for syn in drug.findall('drugbank:synonyms/drugbank:synonym', ns)],
            'affected_organisms': [organism.text for organism in
                                   drug.findall('drugbank:affected-organisms/drugbank:affected-organism', ns)],
            'dosages': [{'form': dosage.find('drugbank:form', ns).text,
                         'route': dosage.find('drugbank:route', ns).text,
                         'strength': dosage.find('drugbank:strength', ns).text}
                        for dosage in drug.findall('drugbank:dosages/drugbank:dosage', ns)],
            'food_interactions': [interaction.text for interaction in
                                  drug.findall('drugbank:food-interactions/drugbank:food-interaction', ns)],
            'drug_interactions': [{'name': interaction.find('drugbank:name', ns).text,
                                   'description': interaction.find('drugbank:description', ns).text}
                                  for interaction in
                                  drug.findall('drugbank:drug-interactions/drugbank:drug-interaction', ns)],
            'external_link': drug.find('drugbank:external-link', ns).text if drug.find('drugbank:external-link',
                                                                                       ns) is not None else None,
            'pathways': [{'name': pathway.find('drugbank:name', ns).text,
                          'smpdb-id': pathway.find('drugbank:smpdb-id', ns).text,
                          'category': pathway.find('drugbank:category', ns).text}
                         for pathway in drug.findall('drugbank:pathways/drugbank:pathway', ns)],
        }

        drugs_info.append(drug_info)

    return drugs_info, kingdoms, superclasses, classes


# Example usage
def createData():
    file_path = './data/full database.xml'
    drugs, kingdoms, superclasses, classes = extract_drug_info(file_path)

    save_to_pickle(drugs, './data/extracted-drugs.pkl')
    save_to_json(drugs, './data/extracted-drugs.json')

    for kingdom in kingdoms:
        print(kingdom)

    for sc in superclasses:
        print(sc)

    for c in classes:
        print(c)


def extract_classification_sets(drugs):
    kingdoms = set()
    superclasses = set()
    classes = set()

    for drug in drugs:
        classification = drug.get('classification', {})
        if classification:
            if classification.get('kingdom'):
                kingdoms.add(classification['kingdom'])
            if classification.get('superclass'):
                superclasses.add(classification['superclass'])
            if classification.get('class'):
                classes.add(classification['class'])

    return kingdoms, superclasses, classes

def printDataItems(data):
    for item in data:
        print(item)

def main():
    data = load_from_pickle('./data/extracted-drugs.pkl')

    kingdoms, superclasses, classes = extract_classification_sets(data)

    print("=== KINGDOMS ===")
    printDataItems(kingdoms)
    print("=== SUPERCLASSES ===")
    printDataItems(superclasses)
    print("=== CLASSES ===")
    printDataItems(classes)

if __name__ == '__main__':
    main()