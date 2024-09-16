import networkx as nx


def update_graph_save_locally(plants, families, relationships, output_path="../plants/output/ plants_graph.graphml"):
    graph = nx.read_graphml(output_path)
    root_node = 'Families'

    for plant in plants:
        if not graph.has_node(plant):
            authors_str = ','.join(plant['authors'])
            graph.add_node(plant['symbol'], name=plant['scientific_name'], type='plant', common_name=plant['common_name'], authors=authors_str)
    for family in families:
        if not graph.has_node(family):
            graph.add_node(family, type='family')

    for relationship in relationships:
        plant_node = relationship['scientific_name']
        family_node = relationship['family_name']
        if not graph.has_edge(plant_node, family_node):
            graph.add_edge(family_node, plant_node)

    for family in families:
        if not graph.has_edge(root_node, family):
            graph.add_edge(root_node, family)

    nx.write_graphml(graph, output_path)


def create_graph_save_locally(plants, families, relationships, output_path):
    graph = nx.Graph()

    root_node = 'Families'
    graph.add_node(root_node, type='root')

    for plant in plants:
        authors_str = ','.join(plant['authors'])
        graph.add_node(plant['symbol'], name=plant['scientific_name'], type='plant', common_name=plant['common_name'], authors=authors_str)

    for family in families:
        graph.add_node(family, type='family')

    for relationship in relationships:
        plant_node = relationship['scientific_name']
        family_node = relationship['family_name']
        graph.add_edge(family_node, plant_node)

    for family in families:
        graph.add_edge(root_node, family)

    nx.write_graphml(graph, output_path)
    print(f"Graph saved to {output_path}")
