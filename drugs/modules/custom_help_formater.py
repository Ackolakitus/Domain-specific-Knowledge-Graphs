import argparse


class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if action.option_strings:
            return ', '.join(action.option_strings)
        return action.dest


def create_or_update_save_locally_args():
    parser = argparse.ArgumentParser(description="Graph operations with local storage.",
                                     formatter_class=CustomHelpFormatter)

    parser.add_argument("-if", "--input_file",
                        help="Dataset txt/csv file path or Graph file path.",
                        required=True,
                        type=str)
    parser.add_argument("-a", "--action",
                        choices=["create", "update"],
                        help="Action to perform on the graph.",
                        required=True, type=str)
    parser.add_argument("-of", "--output_file",
                        help="Output file name.",
                        default="./output/drugs_and_diseases_graph.graphml")
    return parser.parse_args()


def create_or_update_save_neo4j_args():
    parser = argparse.ArgumentParser(description="Graph operations with Neo4j storage.",
                                     formatter_class=CustomHelpFormatter)

    parser.add_argument("-if", "--input_file",
                        help="Dataset txt/csv file path or Graph file path.",
                        required=True,
                        type=str)
    parser.add_argument("-a", "--action",
                        choices=["create", "update", "delete"],
                        help="Action to perform on the graph.",
                        required=True, type=str)
    return parser.parse_args()