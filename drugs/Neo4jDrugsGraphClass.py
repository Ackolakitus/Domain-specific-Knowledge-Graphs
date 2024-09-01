import neo4j.exceptions
from neo4j import GraphDatabase


# CREATE INDEX FOR (p:Plant) ON (p.scientific_name);
def create_constraints(tx):
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (k:Kingdom) REQUIRE k.name IS UNIQUE ")
    # tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (spc:Superclass) REQUIRE spc.name IS UNIQUE ")
    # tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Class) REQUIRE c.name IS UNIQUE ")
    # tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (sbc:Subclass) REQUIRE sbc.name IS UNIQUE ")
    # tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Parent) REQUIRE p.name IS UNIQUE ")
    # tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE")


def add_root_node(tx):
    """
    Add a root node labeled 'Root' with the name 'Kingdoms'.
    """
    query = "MERGE (r:Root {name: 'Kingdoms'})"
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
            "SET d.drugbank-id=$id d.type = $type, d.state = $state, d.groups = $groups, d.salts = $salts, d.affected_organisms = $affected_organisms, d.external_links = $external_links"
        )
        try:
            tx.run(query, name=drug['name'], id=drug['drugbank-id'], type=drug['type'],
                   state=drug['state'], groups=drug['groups'], salts=drug['salts'], affected_organisms=drug['affected_organisms'], external_links=drug['external_links'])
        except neo4j.exceptions.TransactionError:
            continue


def add_or_update_relationships(tx, relationships):
    """
    Create relationship between any 2 types of nodes.
    """
    for rel in relationships:
        query = (
            "MATCH (a:$a_type {name: $a_name}), (b:$b_type {name: $b_name})"
            "MERGE (a)-[:HAS_$relationship]->(b)"
        )
        tx.run(query, a_type=rel[0], a_name=rel[1], b_type=rel[2], b_name=rel[3], relationship=str(rel[2]).upper())


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
    query = """
    MATCH (n:$type {name: $name})
    DETACH DELETE n
    """
    tx.run(query, type=node_type, name=node_name)


def delete_relationship(tx, relationship):
    """
    Delete the relationship between 2 nodes of any type.
    """
    if len(relationship) != 4:
        print("Invalid relationship format")
        return

    query = """
            MATCH (a:$a_type {name: $a_name})-[r:HAS_$relationship]->(b:$b_type {name: $b_name})
            DELETE r
            """
    tx.run(query,
           a_type=relationship[0],
           a_name=relationship[1],
           b_type=relationship[2],
           b_name=relationship[3],
           relationship=str(relationship[2]).upper())

# MATCH (s:Superclass)-[r*0..]->(n)
# WHERE s.name = $superclassName
# AND (type(r) IN ['HAS_CLASS', 'HAS_SUBCLASS', 'HAS_DRUG'])
# RETURN DISTINCT n

# def delete_node_and_nodes_belonging(tx, node_type, node_name):
#     """
#     Delete a type of node by its name and all nodes belonging to it.
#     """
#     delete_nodes_query = """
#             MATCH (p:Plant)-[:BELONGS_TO]->(n:$type {name: $name})
#             DETACH DELETE p
#             """
#     tx.run(delete_nodes_query, type=node_type, name=node_name)
#
#     delete_node_query = """
#             MATCH (n:$type {name: $name})
#             DETACH DELETE n
#             """
#     tx.run(delete_node_query, type=node_type, name=node_name)


# def print_plant_node_details(node):
#     (node_id, node_props) = node
#     print(f"Plant: {node_props['scientific_name']}\n"
#           f"Symbol: {node_props['symbol']}\n"
#           f"Common name: {node_props['common_name']}\n"
#           f"Other names: {node_props['other_names']}\n"
#           f"Authors: {node_props['authors']}")


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
            # self.driver.verify_connectivity()
        except neo4j.exceptions.ConfigurationError:
            print("URI format is not supported! Check your uri environment variable.")
        except neo4j.exceptions.AuthError:
            print("Authentication failure! Check your auth environment variables.")
        except neo4j.exceptions.ServiceUnavailable:
            print("Could not establish a connection with Neo4j database!")
        except ValueError:
            print("Unknown exception")

        with self.driver.session() as session:
            # try:
            session.write_transaction(create_constraints)
            # except neo4j.exceptions.ClientError as e:
            #     print(f"{e.message}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the connection to the Neo4j database.
        """
        if self.driver:
            self.driver.close()

    def create_or_update_graph(self, drugs, kingdoms, superclasses, classes, subclasses, parents, relationships, batch_size=300):
        """
        Save the graph data into the Neo4j database.

        Steps:\n
        1. Add a root node labeled 'Root' with the name 'Kingdoms'.
        2. Add classification nodes to the root node in batches.
        3. Add drug nodes to the classification nodes in batches.
        4. Add relationships between nodes in batches.

        :param drugs: List of drugs dictionaries with attributes.
        :param kingdoms: List of kingdoms names.
        :param superclasses: List of superclasses names.
        :param classes: List of classes names.
        :param subclasses: List of subclasses names.
        :param relationships: List of all relationships .
        :param batch_size: Number of items to process per batch (default: 300).
        """
        with self.driver.session() as session:
            try:
                session.execute_write(add_root_node)
            except neo4j.exceptions.ConstraintError:
                pass

            def process_batches(items, batch_func):
                total_items = len(items)
                for i in range(0, total_items, batch_size):
                    end_index = min(i + batch_size, total_items)
                    batch = items[i:end_index]
                    try:
                        session.execute_write(batch_func, batch)
                    except neo4j.exceptions.ConstraintError:
                        pass
                    print(f"Processed items from {i} to {i + len(batch)}")

            process_batches(kingdoms, add_kingdom_nodes)
            process_batches(superclasses, add_superclass_nodes)
            process_batches(classes, add_class_nodes)
            process_batches(subclasses, add_subclass_nodes)
            process_batches(parents, add_parent_nodes)

            process_batches(drugs, add_or_update_drug_nodes)
            process_batches(relationships, add_or_update_relationships)

    # def deleteDataFromGraph(self, plants, families, deleteFamily):
    #     with self.driver.session() as session:
    #         if deleteFamily:
    #             session.execute_write(delete_family_and_nodes_belonging, families)
    #         else:
    #             for plant in plants:
    #                 session.execute_write(delete_plant_node, plant)
    #
    # def get_plants_nodes_belonging_to_family(self, family_name):
    #     """
    #     Get plant nodes belonging to a specific family.
    #     :param family_name: Name of the family to search for.
    #     :return: List of nodes belonging to the family.
    #     """
    #     query = """
    #             MATCH (n)-[:BELONGS_TO]->(m {name: $name})
    #             RETURN elementId(n) AS node_id, n
    #             """
    #     with self.driver.session() as session:
    #         result = session.run(query, name=family_name)
    #         nodes = [(record["node_id"], record["n"]) for record in result]
    #     return nodes
    #
    # def get_plant_node(self, plantName):
    #     query = """
    #         MATCH (p:Plant {scientific_name: $scientific_name})
    #         RETURN elementId(p) AS node_id, p
    #     """
    #     with self.driver.session() as session:
    #         result = session.run(query, scientific_name=plantName)
    #         record = result.single()
    #         node = (record["node_id"], record["p"])
    #     return node
    #
    # def deleteFamilyNode(self, familyName):
    #     with self.driver.session() as session:
    #         session.execute_write(delete_family_node, familyName)
    #
    # def deletePlantNode(self, plantName):
    #     with self.driver.session() as session:
    #         session.execute_write(delete_plant_node, plantName)
    #
    # def deleteFamilyAndNodesBelonging(self, familyName):
    #     with self.driver.session() as session:
    #         session.execute_write(delete_family_and_nodes_belonging, familyName)

# with Neo4jGraphClass(uri, user, password) as neo4j_query:
# nodes = neo4j_query.find_nodes_belonging_to_family("Moringaceae")
# nodes = neo4j_query.find_nodes_belonging_to_family("Apiaceae")
# for node in nodes:
#     print(node)
# print(node["n"]["element_id"])
# print(node['node_id'])
