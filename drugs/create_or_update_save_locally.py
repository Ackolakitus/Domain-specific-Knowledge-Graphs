import os
import sys
from modules.extract_data import create_graph_save_locally, update_graph_save_locally
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
        create_graph_save_locally(args.input_file)
    elif args.action == "update":
        update_graph_save_locally(args.input_file, args.graph_file, args.output_file)


if __name__ == '__main__':
    main()
