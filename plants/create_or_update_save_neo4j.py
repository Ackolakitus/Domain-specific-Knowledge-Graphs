import os
import logging
import sys
from pathlib import Path
from modules.dataset_functions import getDataFromRows, getRowsPreprocessedDataset
from modules.custom_help_formater import create_or_update_save_neo4j_args
from dotenv import load_dotenv
from modules.Neo4jPlantsGraphClass import Neo4jGraphClass, print_plant_node_details


def load_env_vars():
    env_path = Path('..', 'proba.env')
    load_dotenv(dotenv_path=env_path)

    uri = os.getenv("URI_PLANTS")
    user = os.getenv("USER_PLANTS")
    password = os.getenv("PASSWORD_PLANTS")

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
        print(f"The 'URI_PLANTS' environment variable is missing or is not a non-empty string.")
        sys.exit(1)

    if not isinstance(user, str) or not user:
        print(f"The 'USER_PLANTS' environment variable is missing or is not a non-empty string.")
        sys.exit(1)

    if not isinstance(password, str) or not password:
        print(f"The 'PASSWORD_PLANTS' environment variable is missing or is not a non-empty string.")
        sys.exit(1)

    if args.action in ["create", "update"]:
        try:
            with Neo4jGraphClass(uri, user, password) as neo4j:
                data_rows = getRowsPreprocessedDataset(args.input_file)
                plants, families, relationships = getDataFromRows(data_rows)

                neo4j.create_or_update_graph(plants, families, relationships, batch_size=200)
        except ValueError as e:
            print(e.args[0])
    elif args.action == "delete":
        del_family = True if args.option == "with" else False
        try:
            with Neo4jGraphClass(uri, user, password) as neo4j:
                data_rows = getRowsPreprocessedDataset(args.input_file)
                plants, families = getDataFromRows(data_rows)

                neo4j.delete_data_from_graph(plants, families, del_family)
        except ValueError as e:
            print(e.args[0])


def debug():
    uri, user, password = load_env_vars()

    data_rows = getRowsPreprocessedDataset("data/plants.csv")
    plants, families, relationships = getDataFromRows(data_rows)

    print(f"Plants {len(plants)}")
    print(f"Families {len(families)}")
    print(f"Relationships {len(relationships)}")

    try:
        with Neo4jGraphClass(uri, user, password) as neo4j:
            neo4j.create_or_update_graph(plants, families, relationships, batch_size=200)
            plant = neo4j.get_plant_node("Abroma augustum")
            print_plant_node_details(plant)
    except ValueError as e:
        print(e.args[0])


if __name__ == '__main__':
    # main()
    debug()
