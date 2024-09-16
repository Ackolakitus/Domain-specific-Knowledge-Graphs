import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from modules.custom_help_formater import create_or_update_save_neo4j_args
from modules.Neo4jDrugsGraphClass import Neo4jGraphClass
from modules.extract_data import extract_drug_info, create_disease_nodes_and_relations, create_classification_relationships, load_from_pickle, create_classification_sets

def load_env_vars():
    env_path = Path('..', 'proba.env')
    load_dotenv(dotenv_path=env_path)

    uri = os.getenv("URI_DRUGS")
    user = os.getenv("USER_DRUGS")
    password = os.getenv("PASSWORD_DRUGS")

    return uri, user, password

def main():
    args = create_or_update_save_neo4j_args()
    logging.basicConfig(level=logging.ERROR)

    if not os.path.isfile(args.input_file):
        print(f"The file {args.input_file} does not exist.")
        sys.exit(1)

    if args.action not in ["create", "update", "delete"]:
        print(f"Choose from actions [ create / update / delete].")
        sys.exit(1)

    uri, user, password = load_env_vars()

    if not isinstance(uri, str) or not uri:
        print(f"The 'URI_DRUGS' environment variable is missing or is not a non-empty string.")
        sys.exit(1)

    if not isinstance(user, str) or not user:
        print(f"The 'USER_DRUGS' environment variable is missing or is not a non-empty string.")
        sys.exit(1)

    if not isinstance(password, str) or not password:
        print(f"The 'PASSWORD_DRUGS' environment variable is missing or is not a non-empty string.")
        sys.exit(1)

    if args.action in ["create", "update"]:
        try:
            biotech, small_molecule, kingdoms, superclasses, classes, subclasses, parents = extract_drug_info(args.input_file)

            drugs = biotech + small_molecule
            relations = create_classification_relationships(drugs)

            diseases, disease_relations = create_disease_nodes_and_relations(drugs)

            with Neo4jGraphClass(uri, user, password) as neo4j:
                neo4j.create_or_update_graph(drugs, kingdoms, superclasses, classes, subclasses, parents, relations,
                                             diseases,
                                             disease_relations, 200)
        except ValueError as e:
            print(e.args[0])
    # elif args.action == "delete":
    #     try:
    #         with Neo4jGraphClass(uri, user, password) as neo4j:
    #
    #     except ValueError as e:
    #         print(e.args[0])


def debug():
    uri, user, password = load_env_vars()

    biotech = load_from_pickle('data/extracted-biotech-drugs.pkl')
    small_molecule = load_from_pickle('data/small-molecule-drugs.pkl')

    drugs = biotech + small_molecule

    kingdoms, superclasses, classes, subclasses, parents = create_classification_sets(drugs)

    relations = create_classification_relationships(drugs)

    diseases, disease_relations = create_disease_nodes_and_relations(drugs, "./data/extracted-diseases.pkl", "./data/extracted-disease-drug.tsv")

    with Neo4jGraphClass(uri, user, password) as neo4j:
        neo4j.create_or_update_graph(drugs, kingdoms, superclasses, classes, subclasses, parents, relations,
                                     diseases,
                                     disease_relations, 200)


if __name__ == '__main__':
    main()
    # debug()
