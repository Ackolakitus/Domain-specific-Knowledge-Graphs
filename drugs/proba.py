# import os
# from pathlib import Path
# from dotenv import load_dotenv
# import pandas as pd
# import csv
#
# from Neo4jDrugsGraphClass import Neo4jGraphClass
# from drugs.extract_data import create_classification_sets
# from extract_data import create_classification_relationships, load_from_pickle, create_disease_nodes_and_relations
#
#
# def print_data_items(data):
#     for item in data:
#         print(item)
#
#
# def loadEnvVars():
#     env_path = Path('..', 'proba.env')
#     load_dotenv(dotenv_path=env_path)
#
#     uri = os.getenv("URI_DRUGS")
#     user = os.getenv("USER_DRUGS")
#     password = os.getenv("PASSWORD_DRUGS")
#
#     return uri, user, password
#
#
# def main():
#     uri, user, password = loadEnvVars()
#
#     biotech = load_from_pickle('./data/extracted-biotech-drugs.pkl')
#     small_molecule = load_from_pickle('./data/small-molecule-drugs.pkl')
#
#     drugs = biotech + small_molecule
#
#     biotech_rels = create_classification_relationships(biotech)
#     small_molecule_rels = create_classification_relationships(small_molecule)
#
#     relations = biotech_rels.union(small_molecule_rels)
#
#     kingdoms1, superclasses1, classes1, subclasses1, parents1 = create_classification_sets(biotech)
#     kingdoms2, superclasses2, classes2, subclasses2, parents2 = create_classification_sets(small_molecule)
#
#     kingdoms = kingdoms1 | kingdoms2
#     superclasses = superclasses1 | superclasses2
#     classes = classes1 | classes2
#     subclasses = subclasses1 | subclasses2
#     parents = parents1 | parents2
#
#     diseases, disease_relations = create_disease_nodes_and_relations(drugs)
#
#     with Neo4jGraphClass(uri, user, password) as neo4j:
#         neo4j.create_or_update_graph(drugs, kingdoms, superclasses, classes, subclasses, parents, relations, diseases,
#                                      disease_relations, 200)
#
#
# if __name__ == '__main__':
#     main()
