import analyzer
import networkx as nx
import matplotlib.pyplot as plt


def relation_plot():
    an = analyzer.Analyzer()

    with open("./friends_list.txt", mode="r", encoding="utf-8") as f:
        friends_list = set(a.strip() for a in f.readlines())

    player_count = {}
    for world_name, _, pls in an.players:
        if world_name == "VRChat Home":
            continue
        S = set(pl for _, _, pl in pls)
        for s in S:
            player_count[s] = player_count.setdefault(s, 0) + 1

    nodes = [(name, {"count": min(100, count)}) for name, count in player_count.items() if count > 4 and name in friends_list]
    print(len(nodes))

    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    name_to_id = {name: i for i, (name, _) in enumerate(nodes)}
    for name, to_join in an.relation.items():
        if name not in name_to_id:
            continue

        for pl, weight in to_join.items():
            if pl not in name_to_id:
                continue
            if weight < 2:
                continue
            if pl == "cleantted":
                continue
            G.add_edge(name, pl, weight=weight)

    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(G, k=1.9, seed=2)
    node_size = [ d['count']*200 for (n,d) in G.nodes(data=True)]
    nx.draw_networkx_nodes(G, pos, node_color='b', alpha=0.2, node_size=node_size)
    nx.draw_networkx_labels(G, pos, font_size=22, font_weight="bold", font_family='IPAPGothic')

    edge_color = [ 'r' if d['weight'] > 10 else 'g' if d['weight'] > 5 else 'blue' if d['weight'] > 1 else 'white' for (_, _, d) in G.edges(data=True)]

    edge_width = [ d['weight'] * 0.9 for (u,v,d) in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color=edge_color, width=edge_width)
    plt.axis("off")
    plt.savefig("output.png")


if __name__ == "__main__":
    relation_plot()
    pass