import neo4j.exceptions
from neo4j import GraphDatabase


# CREATE INDEX FOR (p:Plant) ON (p.scientific_name);
def create_constraints(tx):
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Family) REQUIRE f.name IS UNIQUE ")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Plant) REQUIRE p.scientific_name IS UNIQUE")


def add_root_node(tx):
    """
    Add a root node labeled 'Root' with the name 'Families'.
    """
    query = "MERGE (r:Root {name: 'Families'})"
    tx.run(query)


def add_family_nodes(tx, families):
    """
    Add family nodes for each family in the list.
    """
    for family in families:
        query = "MERGE (f:Family {name: $name})"
        try:
            tx.run(query, name=family)
        except neo4j.exceptions.TransactionError:
            continue


def add_or_update_plant_nodes(tx, plants):
    """
    Add plant nodes with given attributes.
    """
    for plant in plants:
        query = (
            "MERGE (p:Plant {scientific_name: $scientific_name}) "
            "SET p.common_name = $common_name, p.other_names = $other_names, p.authors = $authors, p.symbol = $symbol "
        )
        try:
            tx.run(query, scientific_name=plant['scientific_name'], common_name=plant['common_name'],
                   other_names=plant['other_names'], authors=plant['authors'], symbol=plant['symbol'])
        except neo4j.exceptions.TransactionError:
            continue


def add_or_update_relationships(tx, relationships):
    """
    Create relationships between plants and families.
    """
    for rel in relationships:
        query = (
            "MATCH (p:Plant {scientific_name: $scientific_name}), (f:Family {name: $family_name}) "
            "MERGE (p)-[:BELONGS_TO]->(f)"
        )
        tx.run(query, scientific_name=rel['scientific_name'], family_name=rel['family_name'])


def add_root_relationships(tx, families):
    """
    Create relationships between the root node and family nodes.
    """
    for family in families:
        query = (
            "MATCH (r:Root {name: 'Families'}), (f:Family {name: $family_name}) "
            "MERGE (r)-[:CONTAINS]->(f)"
        )
        tx.run(query, family_name=family)


def delete_plant_node(tx, scientific_name):
    """
    Delete a plant node by its scientific name.
    """
    query = """
    MATCH (p:Plant {scientific_name: $scientific_name})
    DETACH DELETE p
    """
    tx.run(query, scientific_name=scientific_name)


def delete_family_node(tx, name):
    """
    Delete a family node by its name.
    """
    query = """
    MATCH (f:Family {name: $name})
    DETACH DELETE f
    """
    tx.run(query, name=name)


def delete_relationship(tx, scientific_name, family_name):
    """
    Delete the relationship between a plant and a family.
    """
    query = """
            MATCH (p:Plant {scientific_name: $scientific_name})-[r:BELONGS_TO]->(f:Family {name: $family_name})
            DELETE r
            """
    tx.run(query, scientific_name=scientific_name, family_name=family_name)


def delete_family_and_nodes_belonging(tx, family_name):
    """
    Delete a family node by its name and all plants nodes of that family.
    """
    delete_plants_query = """
            MATCH (p:Plant)-[:BELONGS_TO]->(f:Family {name: $name})
            DETACH DELETE p
            """
    tx.run(delete_plants_query, name=family_name)

    delete_family_query = """
            MATCH (f:Family {name: $name})
            DETACH DELETE f
            """
    tx.run(delete_family_query, name=family_name)


def print_plant_node_details(node):
    (node_id, node_props) = node
    print(f"Plant: {node_props['scientific_name']}\n"
          f"Symbol: {node_props['symbol']}\n"
          f"Common name: {node_props['common_name']}\n"
          f"Other names: {node_props['other_names']}\n"
          f"Authors: {node_props['authors']}")


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

    def createOrUpdateGraph(self, plants, families, relationships, batch_size=300):
        """
        Save the graph data into the Neo4j database.

        Steps:
        1. Add a root node labeled 'Root' with the name 'Families'.
        2. Add family nodes and relationships to the root node.
        3. Add plant nodes and relationships to family nodes in batches.

        :param plants: List of plant dictionaries with attributes.
        :param families: List of family names.
        :param relationships: List of plant-family relationship dictionaries.
        :param batch_size: Number of items to process per batch (default: 300).
        """
        with self.driver.session() as session:
            try:
                session.execute_write(add_root_node)
            except neo4j.exceptions.ConstraintError:
                pass

            try:
                session.execute_write(add_family_nodes, families)
            except neo4j.exceptions.ConstraintError:
                pass

            try:
                session.execute_write(add_root_relationships, families)
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

            process_batches(plants, add_or_update_plant_nodes)
            process_batches(relationships, add_or_update_relationships)

    def deleteDataFromGraph(self, plants, families, deleteFamily):
        with self.driver.session() as session:
            if deleteFamily:
                session.execute_write(delete_family_and_nodes_belonging, families)
            else:
                for plant in plants:
                    session.execute_write(delete_plant_node, plant)

    def get_plants_nodes_belonging_to_family(self, family_name):
        """
        Get plant nodes belonging to a specific family.
        :param family_name: Name of the family to search for.
        :return: List of nodes belonging to the family.
        """
        query = """
                MATCH (n)-[:BELONGS_TO]->(m {name: $name})
                RETURN elementId(n) AS node_id, n
                """
        with self.driver.session() as session:
            result = session.run(query, name=family_name)
            nodes = [(record["node_id"], record["n"]) for record in result]
        return nodes

    def get_plant_node(self, plantName):
        query = """
            MATCH (p:Plant {scientific_name: $scientific_name})
            RETURN elementId(p) AS node_id, p
        """
        with self.driver.session() as session:
            result = session.run(query, scientific_name=plantName)
            record = result.single()
            node = (record["node_id"], record["p"])
        return node

    def deleteFamilyNode(self, familyName):
        with self.driver.session() as session:
            session.execute_write(delete_family_node, familyName)

    def deletePlantNode(self, plantName):
        with self.driver.session() as session:
            session.execute_write(delete_plant_node, plantName)

    def deleteFamilyAndNodesBelonging(self, familyName):
        with self.driver.session() as session:
            session.execute_write(delete_family_and_nodes_belonging, familyName)

# with Neo4jGraphClass(uri, user, password) as neo4j_query:
# nodes = neo4j_query.find_nodes_belonging_to_family("Moringaceae")
# nodes = neo4j_query.find_nodes_belonging_to_family("Apiaceae")
# for node in nodes:
#     print(node)
# print(node["n"]["element_id"])
# print(node['node_id'])
