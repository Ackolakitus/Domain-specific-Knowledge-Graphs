import os
import sys
from modules.extract_data import extract_drug_info, extract_disease_info, save_drug_data, save_disease_data, create_classification_relationships, create_classification_sets, create_disease_nodes_and_relations, create_graph_save_locally
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
        file_path = '../raw-data/full database.xml'
        biotech, small_molecule, kingdoms, superclasses, classes, subclasses, parents = extract_drug_info(file_path)
        save_drug_data(biotech, small_molecule)

        diseases = extract_disease_info("../raw-data/disease.tsv")
        save_disease_data(diseases)

        all_drugs = biotech + small_molecule

        relations = create_classification_relationships(all_drugs)

        kingdoms, superclasses, classes, subclasses, parents = create_classification_sets(all_drugs)

        disease_nodes, disease_relations = create_disease_nodes_and_relations(all_drugs)



    # elif args.action == "update":
    #
    #
    # rows = getRowsPreprocessedDataset(input_file)
    #
    # plants, families, relationships = getDataFromRows(rows)
    # createGraphSaveLocally(plants, families, relationships)




if __name__ == '__main__':
    main()