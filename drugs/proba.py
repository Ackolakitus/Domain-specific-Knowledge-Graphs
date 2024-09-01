import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
import neo4j.exceptions

from Neo4jDrugsGraphClass import Neo4jGraphClass
from drugs.extract_data import extract_classification_sets
from extract_data import extract_classification_relationships, load_from_pickle

def print_data_items(data):
    for item in data:
        print(item)

def loadEnvVars():
    env_path = Path('..', 'proba.env')
    load_dotenv(dotenv_path=env_path)

    uri = os.getenv("URI_DRUGS")
    user = os.getenv("USER_DRUGS")
    password = os.getenv("PASSWORD_DRUGS")

    return uri, user, password

def main():
    uri, user, password = loadEnvVars()

    biotech = load_from_pickle('./data/extracted-biotech-drugs.pkl')
    small_molecule = load_from_pickle('./data/small-molecule-drugs.pkl')

    drugs = biotech + small_molecule

    biotech_rels = extract_classification_relationships(biotech)
    small_molecule_rels = extract_classification_relationships(small_molecule)

    relations = biotech_rels.union(small_molecule_rels)


    kingdoms1, superclasses1, classes1, subclasses1, parents1 = extract_classification_sets(biotech)

    kingdoms2, superclasses2, classes2, subclasses2, parents2 = extract_classification_sets(small_molecule)

    kingdoms = kingdoms1 | kingdoms2
    superclasses = superclasses1 | superclasses2
    classes = classes1 | classes2
    subclasses = subclasses1 | subclasses2
    parents = parents1 | parents2


    # print_data_items(small_molecule_rels)
    # print(len(drugs))

    print(uri, user, password, sep="\n")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
    except neo4j.exceptions.ServiceUnavailable:
        print("Could not establish a connection with Neo4j database!")
    # with Neo4jGraphClass(uri, user, password) as neo4j:
    #     neo4j.create_or_update_graph(drugs, kingdoms, superclasses, classes, subclasses, relations, parents,200)

if __name__ == '__main__':
    main()