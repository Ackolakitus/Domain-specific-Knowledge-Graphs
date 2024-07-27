import networkx as nx


def updateGraphSaveLocally(input_file, output_path="plants_graph.graphml"):
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


def createGraphSaveLocally(plants, families, relationships, output_path):
    G = nx.Graph()

    root_node = 'Families'
    G.add_node(root_node, type='root')

    for plant in plants:
        G.add_node(plant['scientific_name'], type='plant', common_name=plant['common_name'], authors=plant['authors'])

    for family in families:
        G.add_node(family, type='family')

    for relationship in relationships:
        plant_node = relationship['scientific_name']
        family_node = relationship['family_name']
        G.add_edge(plant_node, family_node)

    nx.write_graphml(G, output_path)
    print(f"Graph saved to {output_path}")
