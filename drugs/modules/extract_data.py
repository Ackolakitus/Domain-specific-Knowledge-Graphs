import sys
import xml.etree.ElementTree as ET
import pickle
import json
import csv
import os
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict
import networkx as nx


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
            kingdom = str(classification.find('drugbank:kingdom', ns).text) if classification.find('drugbank:kingdom', ns) is not None else None
            superclass = str(classification.find('drugbank:superclass', ns).text) if classification.find('drugbank:superclass', ns) is not None else None
            c = classification.find('drugbank:class', ns).text if classification.find('drugbank:class', ns) is not None else 'None'
            subclass = str(classification.find('drugbank:subclass', ns).text) if classification.find('drugbank:subclass', ns) is not None else None
            parent = str(classification.find('drugbank:direct-parent', ns).text) if classification.find('drugbank:direct-parent', ns) is not None else None

            if kingdom is not None:
                kingdoms.add(kingdom.lower().title())

            if superclass is not None:
                superclasses.add(superclass.lower().capitalize())

            if c is not None:
                classes.add(c.lower().capitalize())

            if subclass is not None:
                subclasses.add(subclass.lower().capitalize())

            if parent is not None:
                parents.add(parent.lower().capitalize())

        drug_info = {
            'drugbank-id': drug.find('drugbank:drugbank-id', ns).text,
            'type': drug.attrib.get('type'),
            'name': drug.find('drugbank:name', ns).text.lower().capitalize() if drug.find('drugbank:name',
                                                                                          ns) is not None else None,
            'state': drug.find('drugbank:state', ns).text if drug.find('drugbank:state', ns) is not None else None,
            'groups': [group.text for group in drug.findall('drugbank:groups/drugbank:group', ns)],
            'salts': [salt.find('drugbank:name', ns).text for salt in drug.findall('drugbank:salts/drugbank:salt', ns)],
            'classification': {
                'kingdom': str(classification.find('drugbank:kingdom', ns).text).lower().title() if classification is not None else None,
                'superclass': str(classification.find('drugbank:superclass',
                                                      ns).text).lower().capitalize() if classification is not None else None,
                'class': str(classification.find('drugbank:class',
                                                 ns).text).lower().capitalize() if classification is not None else None,
                'subclass': str(classification.find('drugbank:subclass',
                                                    ns).text).lower().capitalize() if classification is not None else None,
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
            'external_links': [link.findtext('drugbank:url', None, ns) for link in drug.findall('drugbank:external-links/drugbank:external-link', ns)],
        }

        if type == 'biotech':
            biotech_info.append(drug_info)
        elif type == 'small molecule':
            small_molecules_info.append(drug_info)

    return biotech_info, small_molecules_info, kingdoms, superclasses, classes, subclasses, parents.difference(kingdoms, superclasses, classes, subclasses)


def save_drug_data(biotech_drugs, small_molecule_drugs):
    save_to_pickle(biotech_drugs, '../data/extracted-biotech-drugs.pkl')
    save_to_json(biotech_drugs, '../data/extracted-biotech-drugs.json')

    save_to_pickle(small_molecule_drugs, '../data/small-molecule-drugs.pkl')
    save_to_json(small_molecule_drugs, '../data/small-molecule-drugs.json')


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


def create_classification_sets(drugs):
    kingdoms = set()
    superclasses = set()
    classes = set()
    subclasses = set()
    parents = set()

    for drug in drugs:
        classification = drug.get('classification', {})
        if classification:
            if (kingdom := classification.get('kingdom')) != 'None':
                kingdoms.add(kingdom.lower().title())
            if (superclass := classification.get('superclass')) != 'None':
                superclasses.add(superclass.lower().capitalize())
            if (class_ := classification.get('class')) != 'None':
                classes.add(class_.lower().capitalize())
            if (subclass := classification.get('subclass')) != 'None':
                subclasses.add(subclass.lower().capitalize())
            if (parent := classification.get('parent')) != 'None':
                parents.add(parent.lower().capitalize())

    return kingdoms, superclasses, classes, subclasses, parents.difference(kingdoms, superclasses, classes, subclasses)


def print_data_items(data):
    for item in data:
        print(item)


def print_data_items_count(data):
    for item, count in data.items():
        print(f"{item}: {count} items")


def create_classification_relationships(drugs):
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
                if any(key != "parent" and value.lower() == direct_parent.lower() for key, value in
                       classification.items()):
                    relationships_set.add(
                        (last_classification_type, last_classification_value, 'Drug', drug.get('name')))
                else:
                    relationships_set.add(
                        (last_classification_type, last_classification_value, 'Parent', direct_parent))
                    relationships_set.add(('Parent', direct_parent, 'Drug', drug.get('name')))
            else:
                relationships_set.add((last_classification_type, last_classification_value, 'Drug', drug.get('name')))
        else:
            relationships_set.add(('Unclassified', 'Unclassified', 'Drug', drug.get('name')))

    relationships_set.add(('Root', 'Kingdoms', 'Unclassified', 'Unclassified'))
    return relationships_set


def print_relations_neo4j(data):
    for item in data:
        print(f'MATCH (a:{item[0]} {{name: {item[1]}}}), (b:{item[2]} {{name: {item[3]}}})')
        print(f'MERGE (a)-[:HAS_{str(item[2]).upper()}]->(b)')


def print_drugs(drugs):
    for drug in drugs:
        print(drug.get('name'))


def create_interaction_relationships(drugs, type):
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


def extract_disease_info(filepath):
    diseases = []
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            mesh_id = row['MESH_ID'].replace('MESH:', '')
            if "D" in mesh_id:
                diseases.append({
                    'name': row['Name'],
                    'doid': mesh_id,
                    'definition': row['Definitions'],
                    'synonyms': row['Synonyms'].split("|"),
                })

    return diseases


def save_disease_data(diseases):
    sorted_diseases = sorted(diseases, key=lambda k: k['doid'])

    save_to_json(sorted_diseases, "../data/extracted-diseases.json")
    save_to_pickle(sorted_diseases, '../data/extracted-diseases.pkl')


def create_disease_nodes_and_relations(drugs, extracted_diseases = "../data/extracted-diseases.pkl", diseases_file_path = '../data/extracted-disease-drug.tsv'):
    diseases = load_from_pickle(extracted_diseases)

    drug_names = {d['drugbank-id']: d['name'] for d in drugs}
    disease_names = {d['doid']: d['name'] for d in diseases}

    diseases_set = set()
    relationships_set = set()

    rows = []

    with open(diseases_file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            rows.append(row)
            diseases_set.add(row['Disease'])

    for row in rows:
        disease_name = disease_names[row['Disease']]
        drug_name = drug_names[row['Drug']]
        relationships_set.add(('Disease', disease_name, 'Drug', drug_name))

    diseases_to_create = [d for d in diseases if d['doid'] in diseases_set]

    return diseases_to_create, relationships_set


def loadEnvVars():
    env_path = Path('../..', 'proba.env')
    load_dotenv(dotenv_path=env_path)

    uri = os.getenv("URI_DRUGS")
    user = os.getenv("USER_DRUGS")
    password = os.getenv("PASSWORD_DRUGS")

    return uri, user, password


def create_graph_save_locally(file_path, output_path = '../data/drugs_diseases_graph.graphml'):
    biotech, small_molecule, kingdoms, superclasses, classes, subclasses, parents = extract_drug_info(file_path)
    save_drug_data(biotech, small_molecule)

    drugs = biotech + small_molecule

    graph = nx.Graph()
    root_node = 'Kingdoms'
    graph.add_node(root_node, type='root')

    graph.add_nodes_from(kingdoms, type='kingdom')
    graph.add_nodes_from(superclasses, type='superclass')
    graph.add_nodes_from(classes, type='class')
    graph.add_nodes_from(subclasses, type='subclass')
    graph.add_nodes_from(parents, type='parent')

    for drug in drugs:
        groups_str = ','.join(drug['groups']) if drug['groups'] else ''
        salts_str = ','.join(drug['salts']) if drug['salts'] else ''
        affected_orgs_str = ','.join(drug['affected_organisms']) if drug['affected_organisms'] else ''
        links_str = ','.join(drug['external_links']) if drug['external_links'] else ''

        graph.add_node(drug['name'], id=drug['drugbank-id'], type=drug['type'],
                       state=drug['state'] if drug['state'] else '', groups=groups_str, salts=salts_str, affected_organisms=affected_orgs_str, external_links=links_str)


    drug_relations = create_classification_relationships(drugs)

    for relation in drug_relations:
        graph.add_edge(relation[1], relation[3], type=f'HAS_{str(relation[2]).upper()}')

    diseases, disease_relations = create_disease_nodes_and_relations(drugs)
    for disease in diseases:
        synonyms_str = ','.join(disease['synonyms'])
        graph.add_node(disease['name'], id=disease['doid'], definition=disease['definition'],synonyms=synonyms_str)

    for relation in disease_relations:
        graph.add_edge(relation[1], relation[3], type='INDICATES')


    nx.write_graphml(graph, output_path)
    print(f"Graph saved to {output_path}")

def update_graph_save_locally(input_file, graph_file, output_file):
    graph = nx.read_graphml(graph_file)

    biotech, small_molecule, kingdoms, superclasses, classes, subclasses, parents = extract_drug_info(input_file)

    drugs = biotech + small_molecule

    def add_or_update_nodes(items, type):
        for item in items:
            if not graph.has_node(item):
                graph.add_node(item, type=type)

    add_or_update_nodes(kingdoms, 'kingdom')
    add_or_update_nodes(superclasses, 'superclass')
    add_or_update_nodes(classes, 'class')
    add_or_update_nodes(subclasses, 'subclass')
    add_or_update_nodes(parents, 'parent')

    for drug in drugs:
        if not graph.has_node(drug['name']):
            groups_str = ','.join(drug['groups']) if drug['groups'] else ''
            salts_str = ','.join(drug['salts']) if drug['salts'] else ''
            affected_orgs_str = ','.join(drug['affected_organisms']) if drug['affected_organisms'] else ''
            links_str = ','.join(drug['external_links']) if drug['external_links'] else ''

            graph.add_node(drug['name'], id=drug['drugbank-id'], type=drug['type'],
                           state=drug['state'] if drug['state'] else '', groups=groups_str, salts=salts_str,
                           affected_organisms=affected_orgs_str, external_links=links_str)
        # else:
        #     node = graph.nodes[drug['name']]
        #
        #     graph.nodes[drug['name']]['drugbank-id'] = drug['drugbank-id'] if (drug['drugbank-id'] != node[
        #         'drugbank-id']) and (drug['drugbank-id'] != 'None') else node['drugbank-id']
        #     graph.nodes[drug['name']]['type'] = drug['type'] if drug['type'] != node['type'] else node['type']
        #     graph.nodes[drug['name']]['state'] = drug['state'] if drug['state'] != node['state'] else node['state']
        #     graph.nodes[drug['name']]['groups'] = ','.join(drug['groups']) if drug['groups'] else node['groups']
        #     graph.nodes[drug['name']]['salts'] = ','.join(drug['salts']) if drug['salts'] else node['salts']
        #     graph.nodes[drug['name']]['affected_organisms'] = ','.join(drug['affected_organisms']) if drug[
        #         'affected_organisms'] else node['affected_organisms']
        #     graph.nodes[drug['name']]['external_links'] = ','.join(drug['external_links']) if drug[
        #         'external_links'] else node['external_links']

    drug_relations = create_classification_relationships(drugs)

    for relation in drug_relations:
        if not graph.has_edge(relation[1], relation[3]):
            graph.add_edge(relation[1], relation[3], type=f'HAS_{str(relation[2]).upper()}')

    diseases, disease_relations = create_disease_nodes_and_relations(drugs)
    for disease in diseases:
        if not graph.has_node(disease['name']):
            synonyms_str = ','.join(disease['synonyms'])
            graph.add_node(disease['name'], id=disease['doid'], definition=disease['definition'], synonyms=synonyms_str)
        # else:
        #     node = graph.nodes[disease['name']]
        #     graph.nodes[disease['name']]['definition'] = disease['definition'] if disease['definition'] else node['definition']
        #     graph.nodes[disease['name']]['synonyms'] = ','.join(disease['synonyms']) if disease['synonyms'] else node['synonyms']

    for relation in disease_relations:
        if not graph.has_edge(relation[1], relation[3]):
            graph.add_edge(relation[1], relation[3], type='INDICATES')

    nx.write_graphml(graph, output_file)
    print(f"Graph updated and saved to {output_file}")