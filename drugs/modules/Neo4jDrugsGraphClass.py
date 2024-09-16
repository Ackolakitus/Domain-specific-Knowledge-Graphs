import neo4j.exceptions
from neo4j import GraphDatabase

def create_constraints(tx):
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (k:Kingdom) REQUIRE k.name IS UNIQUE ")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:Unclassified) REQUIRE u.name IS UNIQUE ")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (spc:Superclass) REQUIRE spc.name IS UNIQUE ")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Class) REQUIRE c.name IS UNIQUE ")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (sbc:Subclass) REQUIRE sbc.name IS UNIQUE ")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Parent) REQUIRE p.name IS UNIQUE ")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE")


def add_root_node(tx):
    """
    Add a root node labeled 'Root' with the name 'Kingdoms'.
    """
    query = "MERGE (r:Root {name: 'Kingdoms'})"
    tx.run(query)

def add_unclassified_node(tx):
    """
    Add a node labeled 'Unclassified' with the name 'Unclassified'.
    """
    query = "MERGE (u:Unclassified {name: 'Unclassified'})"
    tx.run(query)


def add_kingdom_nodes(tx, kingdoms):
    """
    Add kingdom node for each kingdom in the list.
    """
    for kingdom in kingdoms:
        query = "MERGE (k:Kingdom {name: $name})"
        try:
            tx.run(query, name=kingdom)
        except neo4j.exceptions.TransactionError:
            continue

def add_superclass_nodes(tx, superclasses):
    """
    Add superclass node for each superclass in the list.
    """
    for superclass in superclasses:
        query = "MERGE (spc:Superclass {name: $name})"
        try:
            tx.run(query, name=superclass)
        except neo4j.exceptions.TransactionError:
            continue

def add_class_nodes(tx, classes):
    """
    Add class node for each class in the list.
    """
    for cls in classes:
        query = "MERGE (c:Class {name: $name})"
        try:
            tx.run(query, name=cls)
        except neo4j.exceptions.TransactionError:
            continue

def add_subclass_nodes(tx, subclasses):
    """
    Add subclass node for each subclass in the list.
    """
    for subclass in subclasses:
        query = "MERGE (sbc:Subclass {name: $name})"
        try:
            tx.run(query, name=subclass)
        except neo4j.exceptions.TransactionError:
            continue

def add_parent_nodes(tx, parents):
    """
    Add parent node for each parent in the list.
    """
    for parent in parents:
        query = "MERGE (p:Parent {name: $name})"
        try:
            tx.run(query, name=parent)
        except neo4j.exceptions.TransactionError:
            continue


def add_or_update_drug_nodes(tx, drugs):
    """
    Add drug nodes with given attributes.
    """
    for drug in drugs:
        query = (
            "MERGE (d:Drug {name: $name}) "
            "SET d.drugbank_id=$id, d.type = $type, d.state = $state, d.groups = $groups, d.salts = $salts, d.affected_organisms = $affected_organisms, d.external_links = $external_links"
        )
        try:
            tx.run(query, name=drug['name'], id=drug['drugbank-id'], type=drug['type'],
                   state=drug['state'], groups=drug['groups'], salts=drug['salts'], affected_organisms=drug['affected_organisms'], external_links=drug['external_links'])
        except neo4j.exceptions.TransactionError:
            continue


def add_disease_nodes(tx, diseases):
    """
        Add disease nodes with given attributes.
    """
    for d in diseases:
        query = (
            "MERGE (d:Disease {name: $name}) "
            "SET d.do_id=$id, d.definition = $definition, d.synonyms = $synonyms"
        )
        try:
            tx.run(query, name=d['name'], id=d['doid'], definition=d['definition'],
                   synonyms=d['synonyms'])
        except neo4j.exceptions.TransactionError:
            continue

def add_or_update_relationships(tx, relationships):
    """
    Create relationship between any 2 types of nodes.
    """
    types = {'Unclassified', 'Root', 'Kingdom', 'Superclass', 'Class','Subclass', 'Parent', 'Drug', 'Disease'}

    for rel in relationships:
        if len(rel) != 4 or rel[0] not in types or rel[2] not in types:
            print("Invalid relationship format")
            return

        if rel[0] == 'Disease':
            query = f"MATCH (a:{rel[0]} {{name: \"{rel[1]}\"}}), (b:{rel[2]} {{name: \"{rel[3]}\"}}) MERGE (b)-[:INDICATES]->(a)"
        else:
            query = f"MATCH (a:{rel[0]} {{name: \"{rel[1]}\"}}), (b:{rel[2]} {{name: \"{rel[3]}\"}}) MERGE (a)-[:HAS_{str(rel[2]).upper()}]->(b)"
        tx.run(query)


def delete_drug_node(tx, drug_name):
    """
    Delete a drug node by its name.
    """
    query = """
    MATCH (n:Drug {name: $name})
    DETACH DELETE n
    """
    tx.run(query, name=drug_name)


def delete_any_node(tx, node_type, node_name):
    """
    Delete any node type by its name.
    """
    query = f"MATCH (n:{node_type} {{name: \"{node_name}\"}}) DETACH DELETE n"
    tx.run(query)


def delete_relationship(tx, relationship):
    """
    Delete the relationship between 2 nodes of any type.
    """
    types = {'Unclassified', 'Root', 'Kingdom', 'Superclass', 'Subclass', 'Parent', 'Drug'}

    if len(relationship) != 4 or relationship[0] not in types or relationship[2] not in types:
        print("Invalid relationship format")
        return

    query = (f'MATCH (a:{relationship[0]} {{name: {relationship[1]}}})-[r:HAS_{str(relationship[2]).upper()}]->(b:{relationship[2]} {{name: \"{relationship[3]}\"}})'
             f'DELETE r')
    tx.run(query)


def get_node_and_nodes_belonging(tx, node_type, node_name):
    query = f'MATCH path = (n:{node_type} {{name: "{node_name}"}})-[*]->(n) RETURN nodes(path)'


def get_node_and_nodes_belonging_with_relationships(tx, node_type, node_name):
    query = f'MATCH p=(n:{node_type} {{name: "{node_name}"}})-[*]->() RETURN p'


def print_plant_node_details(node):
    (node_id, node_props) = node
    print(f"Drug name: {node_props['name']}\n"
          f"Drugbank-id: {node_props['drugbank_id']}\n"
          f"Type: {node_props['type']}\n"
          f"Affected organisms: {node_props['affected_organisms']}\n"
          f"State: {node_props['state']}\n"
          f"Groups: {node_props['groups']}\n"
          f"Salts: {node_props['salts']}\n")


class Neo4jGraphClass:
    def __init__(self, uri, user, password):
        """
        Initialize the Neo4jGraphClass with the provided URI, user, and password.
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def __enter__(self):
        """
        Establish a connection to the Neo4j database.
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
        except neo4j.exceptions.ConfigurationError:
            print("URI format is not supported! Check your uri environment variable.")
        except neo4j.exceptions.AuthError:
            print("Authentication failure! Check your auth environment variables.")
        except neo4j.exceptions.ServiceUnavailable:
            print("Could not establish a connection with Neo4j database!")
        except ValueError:
            print("Unknown exception")

        with self.driver.session() as session:
            session.write_transaction(create_constraints)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the connection to the Neo4j database.
        """
        if self.driver:
            self.driver.close()

    def create_or_update_graph(self, drugs, kingdoms, superclasses, classes, subclasses, parents, relationships, diseases, disease_relations, batch_size=300):
        """
        Save the graph data into the Neo4j database.

        Steps:\n
        1. Add a root node labeled 'Root' with the name 'Kingdoms'.
        2. Add 'Unclassified' node for drug nodes that are missing classification.
        3. Add classification and drug nodes in batches.
        4. Add relationships between nodes in batches.

        :param drugs: List of drugs dictionaries with attributes.
        :param kingdoms: List of kingdom node names.
        :param superclasses: List of superclass node names.
        :param classes: List of class node names.
        :param subclasses: List of subclass node names.
        :param parents: List of parent node names.
        :param relationships: List of all relationships.
        :param diseases: List of all diseases.
        :param disease_relations: List of all disease-drug relations.
        :param batch_size: Number of items to process per batch (default: 300).
        """
        with self.driver.session() as session:
            def process_batches(items, batch_func, items_name):
                items_list = list(items)
                total_items = len(items_list)

                for i in range(0, total_items, batch_size):
                    end_index = min(i + batch_size, total_items)
                    batch = items_list[i:end_index]
                    try:
                        session.execute_write(batch_func, batch)
                    except neo4j.exceptions.ConstraintError:
                        pass
                    print(f"Processed {items_name} from {i} to {i + len(batch)}")

            try:
                session.execute_write(add_root_node)
                print(f"Root node added")
                session.execute_write(add_unclassified_node)
                print(f"Unclassified node added")
            except neo4j.exceptions.ConstraintError:
                pass



            process_batches(kingdoms, add_kingdom_nodes, "kingdoms")
            process_batches(superclasses, add_superclass_nodes, "superclasses")
            process_batches(classes, add_class_nodes, "classes")
            process_batches(subclasses, add_subclass_nodes, "subclasses")
            process_batches(parents, add_parent_nodes, "parents")

            process_batches(drugs, add_or_update_drug_nodes, "drugs")
            process_batches(relationships, add_or_update_relationships, "relationships")

            process_batches(diseases, add_disease_nodes, 'diseases')
            process_batches(disease_relations, add_or_update_relationships, 'disease-drug-relations')


