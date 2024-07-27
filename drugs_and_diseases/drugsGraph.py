import os
from dotenv import load_dotenv
import pandas as pd
import networkx as nx
from pyvis.network import Network
from neo4j import GraphDatabase

# Load the data
indications = pd.read_csv('data/indications.tsv', sep='\t')
diseases = pd.read_csv('data/diseases.tsv', sep='\t')
drugs = pd.read_csv('data/drugs.tsv', sep='\t')
# ===============================================================================
# Create a graph
# G = nx.Graph()
#
# # Add disease nodes
# for _, row in diseases.iterrows():
#     G.add_node(row['doid_id'], label=row['disease'], type='disease', title=f"Disease: {row['disease']}")
#
# # Add drug nodes
# for _, row in drugs.iterrows():
#     G.add_node(row['drugbank_id'], label=row['drug'], type='drug', title=f"Drug: {row['drug']}")
#
# # Add edges based on indications
# for _, row in indications.iterrows():
#     G.add_edge(row['doid_id'], row['drugbank_id'], label=row['category'], title=f"Category: {row['category']}")
#
# # ================== Create a pyvis network ==================
# net = Network(notebook=True, width="1920", height="1080")
# net.from_nx(G)
#
# # Customize the appearance
# for node in net.nodes:
#     if node['type'] == 'disease':
#         node['color'] = 'red'
#     elif node['type'] == 'drug':
#         node['color'] = 'blue'
#
# # Show the network
# net.show("pyvis-output/knowledge_graph_drugs_and_diseases.html")
# ===============================================================================

# Print nodes
# print("Nodes:")
# for node, data in G.nodes(data=True):
#     print(f"{node}: {data}")
#
# # Print edges
# print("\nEdges:")
# for u, v, data in G.edges(data=True):
#     print(f"{u} - {v}: {data}")
# Connect to Neo4j

# ===============================================================================
load_dotenv()

uri = os.getenv("URI")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
driver = GraphDatabase.driver(uri, auth=(user, password))


def create_constraints(tx):
    tx.run("CREATE CONSTRAINT FOR (d:Disease) REQUIRE d.doid_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT FOR (d:Drug) REQUIRE d.drugbank_id IS UNIQUE")


def add_disease_nodes(tx, diseases):
    for _, row in diseases.iterrows():
        query = (
            "MERGE (d:Disease {doid_id: $doid_id, name: $name, DM: $DM, SYM: $SYM, NOT: $NOT, total: $total})"
        )
        tx.run(query, doid_id=row['doid_id'], name=row['disease'], DM=row['DM'], SYM=row['SYM'], NOT=row['NOT'],
               total=row['total'])


def add_drug_nodes(tx, drugs):
    for _, row in drugs.iterrows():
        query = (
            "MERGE (d:Drug {drugbank_id: $drugbank_id, name: $name, DM: $DM, SYM: $SYM, NOT: $NOT, total: $total})"
        )
        tx.run(query, drugbank_id=row['drugbank_id'], name=row['drug'], DM=row['DM'], SYM=row['SYM'], NOT=row['NOT'],
               total=row['total'])


def add_indication_relationships(tx, indications):
    for _, row in indications.iterrows():
        query = (
            "MATCH (d:Disease {doid_id: $doid_id}), (r:Drug {drugbank_id: $drugbank_id}) "
            "MERGE (d)-[rel:INDICATES {category: $category, n_curators: $n_curators, n_resources: $n_resources}]->(r)"
        )
        tx.run(query, doid_id=row['doid_id'], drugbank_id=row['drugbank_id'], category=row['category'],
               n_curators=row['n_curators'], n_resources=row['n_resources'])


with driver.session() as session:
    session.write_transaction(create_constraints)
    session.write_transaction(add_disease_nodes, diseases)
    session.write_transaction(add_drug_nodes, drugs)
    session.write_transaction(add_indication_relationships, indications)

print("Graph has been saved to Neo4j!")

driver.close()
# =======================================================================
#   ADD/DELETE/UPDATE THE GRAPH
# def update_or_add_disease_nodes(tx, diseases):
#     for _, row in diseases.iterrows():
#         query = (
#             "MERGE (d:Disease {doid_id: $doid_id}) "
#             "ON CREATE SET d.name = $name, d.DM = $DM, d.SYM = $SYM, d.NOT = $NOT, d.total = $total "
#             "ON MATCH SET d.name = $name, d.DM = $DM, d.SYM = $SYM, d.NOT = $NOT, d.total = $total"
#         )
#         tx.run(query, doid_id=row['doid_id'], name=row['disease'], DM=row['DM'], SYM=row['SYM'], NOT=row['NOT'],
#                total=row['total'])
#
#
# def update_or_add_drug_nodes(tx, drugs):
#     for _, row in drugs.iterrows():
#         query = (
#             "MERGE (d:Drug {drugbank_id: $drugbank_id}) "
#             "ON CREATE SET d.name = $name, d.DM = $DM, d.SYM = $SYM, d.NOT = $NOT, d.total = $total "
#             "ON MATCH SET d.name = $name, d.DM = $DM, d.SYM = $SYM, d.NOT = $NOT, d.total = $total"
#         )
#         tx.run(query, drugbank_id=row['drugbank_id'], name=row['drug'], DM=row['DM'], SYM=row['SYM'], NOT=row['NOT'],
#                total=row['total'])
#
#
# def delete_disease_nodes(tx, disease_ids):
#     for doid_id in disease_ids:
#         query = (
#             "MATCH (d:Disease {doid_id: $doid_id}) "
#             "DETACH DELETE d"
#         )
#         tx.run(query, doid_id=doid_id)
#
#
# # updated_diseases_dataframe i updated_drugs_dataframe se podatocite od fajlovite sto treba da go updejtnat grafot
# with driver.session() as session:
#     # Updating existing nodes
#     session.write_transaction(update_or_add_disease_nodes, updated_diseases_dataframe)
#     session.write_transaction(update_or_add_drug_nodes, updated_drugs_dataframe)
#
#     # Deleting nodes
#     disease_ids_to_delete = [list_of_ids_to_delete]
#     session.write_transaction(delete_disease_nodes, disease_ids_to_delete)
#
#     # Optionally, update relationships or handle other data modifications as needed
#
# print("Graph has been updated in Neo4j!")
#
# driver.close()
