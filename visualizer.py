import analyzer
import configparser
import networkx as nx
import matplotlib.pyplot as plt


def convert_color(value):
    if value > 14:
        return 'r'
    elif value > 7:
        return "g"
    elif value > 4:
        return 'blue' 
    else:
        return 'gray' 


def convert_node_color(name):
    return "black"




def relation_plot(orner_name, home_world):
    an = analyzer.Analyzer(orner_name, home_world)
    an.construct()

    with open("./friends_list.txt", mode="r", encoding="utf-8") as f:
        friends_list = set(a.strip() for a in f.readlines())

    player_count = {}
    for world_name, _, pls in an.players:
        if world_name == home_world:
            continue
        S = set(pl for _, _, pl in pls)
        for s in S:
            player_count[s] = player_count.setdefault(s, 0) + 1
    print(f"player count size: {len(player_count)}")
    nodes = [
        (name, {"count": min(100, count)})    
            for name, count in player_count.items() 
            if count > 5 and name in friends_list
    ]
    print(f"nodes size: {len(nodes)}")

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
            if pl == orner_name:
                continue
            G.add_edge(name, pl, weight=weight)

    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(G, k=1.7, seed=2)
    node_size = [ d['count']*200 for (n,d) in G.nodes(data=True)]
    node_color = [convert_node_color(n) for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_color, alpha=0.5, node_size=node_size)
    nx.draw_networkx_labels(G, pos, font_size=22, font_weight="bold", font_family='IPAPGothic')

    edge_color = [convert_color(d['weight']) for (_, _, d) in G.edges(data=True)]

    edge_width = [ d['weight'] * 0.8 for (u,v,d) in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color=edge_color, width=edge_width)
    plt.axis("off")
    plt.savefig("output.png")


if __name__ == "__main__":
    config_ini = configparser.ConfigParser()
    config_ini.read("./config.ini", encoding="utf-8")

    orner_name = config_ini["setting"]["orner_name"]
    home_world = config_ini["setting"]["home_world"]

    relation_plot(orner_name, home_world)
    pass