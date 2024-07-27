import os
import logging
import sys
from pathlib import Path
from modules.dataset_functions import getDataFromRows, getRowsPreprocessedDataset
from modules.custom_help_formater import create_or_update_save_neo4j_args
from dotenv import load_dotenv
from modules.Neo4jGraphClass import Neo4jGraphClass, print_plant_node_details


def loadEnvVars():
    env_path = Path('..', '.env')
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

    uri, user, password = loadEnvVars()

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
                rowsData = getRowsPreprocessedDataset(args.input_file)
                plants, families, relationships = getDataFromRows(rowsData)

                neo4j.createOrUpdateGraph(plants, families, relationships, batch_size=500)
        except ValueError as e:
            print(e.args[0])
    elif args.action == "delete":
        delFamily = True if args.option == "with" else False
        try:
            with Neo4jGraphClass(uri, user, password) as neo4j:
                rowsData = getRowsPreprocessedDataset(args.input_file)
                plants, families = getDataFromRows(rowsData)

                neo4j.deleteDataFromGraph(plants, families, delFamily)
        except ValueError as e:
            print(e.args[0])


def debug():
    uri, user, password = loadEnvVars()

    # rowsData = getRowsPreprocessedDataset("data/plants.csv")
    # rowsData = getRowsPreprocessedDataset("data/plants_update.csv")
    # plants, families, relationships = getDataFromRows(rowsData)

    # print(f"Plants {len(plants)}")
    # print(f"Families {len(families)}")
    # print(f"Relationships {len(relationships)}")

    try:
        with Neo4jGraphClass(uri, user, password) as neo4j:
            # neo4j.createOrUpdateGraph(plants, families, relationships, batch_size=200)
            plant = neo4j.get_plant_node("Abroma augustum")
            print_plant_node_details(plant)
    except ValueError as e:
        print(e.args[0])


if __name__ == '__main__':
    # main()
    debug()
