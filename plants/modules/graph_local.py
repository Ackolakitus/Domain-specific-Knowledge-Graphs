import networkx as nx


def update_graph_save_locally(input_file, output_path="../plants/output/ plants_graph.graphml"):
    G = nx.Graph()
    #
    # root_node = 'Families'
    # G.add_node(root_node, type='root')
    #
    # rows = getRowsPreprocessedDataset(input_file)
    #
    # for row in rows:
    #     family = row['Family']
    #     name_with_author = row['Scientific Name with Author']
    #     common_name = row['Common Name']
    #     scientific_name = extractPlantName(name_with_author)
    #     authors = extractPlantAuthors(name_with_author)
    #
    #     G.add_node(scientific_name, type='plant',
    #                scientific_name=name_with_author,
    #                common_name=common_name,
    #                authors=authors)
    #
    #     if family:
    #         if family not in G.nodes:
    #             G.add_node(family, type='family')
    #             G.add_edge(root_node, family)
    #         G.add_edge(scientific_name, family)

    nx.write_graphml(G, output_path)


def create_graph_save_locally(plants, families, relationships, output_path):
    graph = nx.Graph()

    root_node = 'Families'
    graph.add_node(root_node, type='root')

    for plant in plants:
        authors_str = ','.join(plant['authors'])
        graph.add_node(plant['scientific_name'], type='plant', common_name=plant['common_name'], authors=authors_str, symbol=plant['symbol'])

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
