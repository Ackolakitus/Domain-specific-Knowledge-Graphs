import os
import sys
from modules.dataset_functions import getDataFromRows, getRowsPreprocessedDataset
from modules.graph_local import create_graph_save_locally
from modules.custom_help_formater import create_or_update_save_locally_args
from modules.graph_local import update_graph_save_locally


def main():
    args = create_or_update_save_locally_args()

    if not os.path.isfile(args.input_file):
        print(f"Error: The file {args.input_file} does not exist.")
        sys.exit(1)

    if args.action not in ["create", "update"]:
        print(f"Error: Choose from actions [ create / update ].")
        sys.exit(1)

    if args.action == "create":
        data_rows = getRowsPreprocessedDataset(args.input_file)
        plants, families, relationships = getDataFromRows(data_rows)
        create_graph_save_locally(plants, families, relationships, args.output_file)
    elif args.action == "update":
        rows = getRowsPreprocessedDataset(args.input_file)

        plants, families, relationships = getDataFromRows(rows)
        update_graph_save_locally(plants, families, relationships)

def debug(input_file, output_file):
    data_rows = getRowsPreprocessedDataset(input_file)
    plants, families, relationships = getDataFromRows(data_rows)
    create_graph_save_locally(plants, families, relationships, output_file)

if __name__ == '__main__':
    main()
    # debug("../plants/data/plants.csv", "../plants/output/plants_graph.graphml")
