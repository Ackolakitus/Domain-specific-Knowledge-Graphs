import os
import argparse
import sys
from modules.dataset_functions import getDataFromRows, getRowsPreprocessedDataset
from modules.graph_local import createGraphSaveLocally
from modules.custom_help_formater import create_or_update_save_locally_args


def main():
    args = create_or_update_save_locally_args()

    if not os.path.isfile(args.input_file):
        print(f"Error: The file {args.input_file} does not exist.")
        sys.exit(1)

    if args.action not in ["create", "update"]:
        print(f"Error: Choose from actions [ create / update ].")
        sys.exit(1)

    if args.action == "create":
        rowsData = getRowsPreprocessedDataset(args.input_file)
        plants, families, relationships = getDataFromRows(rowsData)
        createGraphSaveLocally(plants, families, relationships, args.output_file)
    # elif args.action == "update":
    #
    #
    # rows = getRowsPreprocessedDataset(input_file)
    #
    # plants, families, relationships = getDataFromRows(rows)
    # createGraphSaveLocally(plants, families, relationships)


if __name__ == '__main__':
    main()
