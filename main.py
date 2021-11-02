import configparser
from os import name, sep, makedirs, path
from typing import Counter, DefaultDict, Sequence
import datetime
from analyzer import Analyzer
import xml.etree.ElementTree as ET


invalid_datetime = "9999-99-99 23:59:59"
output_dir = "./output/network"
makedirs(output_dir, exist_ok=True)


def diff_seconds(from_time, to_time):
    date_dt1 = datetime.datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S")
    date_dt2 = datetime.datetime.strptime(to_time, "%Y-%m-%d %H:%M:%S")
    return (date_dt2 - date_dt1).seconds


def relation_in_term(players, orner_name, before, after):
    valid_player_data = filter(
        lambda x: (x[1] != invalid_datetime and before <= x[1] <= after),
        players
    )
    relation = {orner_name: dict()}
    for i, (world, time, pls) in enumerate(valid_player_data):
        for in_time1, out_time1, pl1 in pls:
            for in_time2, out_time2, pl2 in pls:
                if pl1 == pl2:
                    continue
                
                if invalid_datetime in (in_time1, out_time1, in_time2, out_time2):
                    continue

                if in_time1 <= in_time2 <= out_time1 or in_time2 <= in_time1 <= out_time2:
                    sec = diff_seconds(max(in_time1, in_time2), min(out_time1, out_time2))
                    
                    relation[pl1][pl2] = relation.setdefault(pl1, dict()).setdefault(pl2, 0) + sec
                    relation[pl2][pl1] = relation.setdefault(pl2, dict()).setdefault(pl1, 0) + sec
    
    return relation


def chop_user_log():
    config_ini = configparser.ConfigParser()
    config_ini.read("./config.ini", encoding="utf-8")

    orner_name = config_ini["setting"]["orner_name"]
    home_world = config_ini["setting"]["home_world"]

    analyzer = Analyzer(orner_name, home_world)
    analyzer.fetch_world_stay_time()
    analyzer.fetch_players_in_world()

    segment = [
        "2021-01-01 12:00:00",
        # "2021-02-01 12:00:00",
        "2021-03-01 12:00:00",
        # "2021-04-01 12:00:00",
        "2021-05-01 12:00:00",
        # "2021-06-01 12:00:00",
        "2021-07-01 12:00:00",
        # "2021-08-01 12:00:00",
        "2021-09-01 12:00:00",
        # "2021-10-01 12:00:00",
        "2021-11-01 12:00:00",
    ]

    relations = []
    for i in range(len(segment) - 1):
        relations.append(
            relation_in_term(
                analyzer.players,
                orner_name,
                segment[i],
                segment[i + 1],
            )
        )

    names = set()
    for relation in relations:
        names = names.union(set(relation.keys()))
    names = list(names)

    name_dict = {n: i for i, n in enumerate(names)}
    with open(f"{output_dir}/node_list.txt", "w") as f:
        print(*names, sep="\n", file=f)

    for t, relation in enumerate(relations):
        before = segment[t].split()[0]
        after = segment[t + 1].split()[0]
        with open(f"{output_dir}/time_list_separate_{before}_{after}.wlst", "w") as f:
            for i, name1 in enumerate(names):
                if name1 not in relation:
                    continue
                for n, v in relation[name1].items():
                    print(f"{i + 1} {name_dict[n] + 1} {v}", file=f)
    print(f"cleantted's id: {name_dict['cleantted'] + 1}")
    return name_dict["cleantted"] + 1


def create_filtered_list(link_list, allow_node, limit):
    tmp = []
    max_v = 0
    for i, j, v in link_list:
        if i not in allow_node or j not in allow_node:
            continue
        if i >= j:
            continue
        if v < limit:
            continue
        tmp.append((i, j, v - limit))
        max_v = max(max_v, v - limit)
    filtered_list = [
        (i, j, int(v / max_v * 100) + 1) for (i, j, v) in tmp
    ]
    print(len(filtered_list))
    return filtered_list


def connected_list_by(target_id):
    segment = [
        "2021-01-01",
        # "2021-02-01",
        "2021-03-01",
        # "2021-04-01",
        "2021-05-01",
        # "2021-06-01",
        "2021-07-01",
        # "2021-08-01",
        "2021-09-01",
        # "2021-10-01",
        "2021-11-01",
    ]

    with open(f"{output_dir}/node_list.txt", "r") as f:
        node_list = list(n.strip() for n in f.readlines())

    target_list = set()
    for i, after in enumerate(segment[1:]):
        before = segment[i]
        with open(f"{output_dir}/time_list_separate_{before}_{after}.wlst", "r") as f:
            tmp = [tuple(map(int, t.strip().split())) for t in f.readlines()]
        
        for a, b, _ in tmp:
            if a == target_id:
                target_list.add(node_list[b - 1])
            if b == target_id:
                target_list.add(node_list[a - 1])
            
    with open(f"{output_dir}/target_list.txt", "w") as f:
        print(*target_list, sep="\n", file=f)


def output_wlist():
    segment = [
        "2021-01-01",
        # "2021-02-01",
        "2021-03-01",
        # "2021-04-01",
        "2021-05-01",
        # "2021-06-01",
        "2021-07-01",
        # "2021-08-01",
        "2021-09-01",
        # "2021-10-01",
        "2021-11-01",
    ]

    target_list = set()
    if path.exists(f"{output_dir}/target_list.txt"):
        with open(f"{output_dir}/target_list.txt", "r") as f:
            target_list = set(t.strip() for t in f.readlines())

    allow_node = set()
    with open(f"{output_dir}/node_list.txt", "r") as f:
        for i, n in enumerate(f.readlines()):
            if not target_list or n.strip() in target_list:
                allow_node.add(i + 1)

    link_list = []
    for i, after in enumerate(segment[1:]):
        before = segment[i]
        with open(f"{output_dir}/time_list_separate_{before}_{after}.wlst", "r") as f:
            tmp = [tuple(map(int, t.strip().split())) for t in f.readlines()]

        with open(f"{output_dir}/filtered_link_{before}_{after}.wlst", "w") as f:
            for i, j, v in create_filtered_list(tmp, allow_node, 30 * 60):
                print(f"{i} {j} {v}", sep="\n", file=f)
        link_list += tmp
    
    filtered_list = create_filtered_list(link_list, allow_node, 2 * 60 * 60)
    with open(f"{output_dir}/filtered_link_all.wlst", "w") as f:
        for i, j, v in filtered_list:
            print(f"{i} {j} {v}", sep="\n", file=f)


def put_name():
    target = "fixed_clique_2021-09-01_2021-11-01"
    with open(f"{output_dir}/{target}.txt", "r") as f:
        group_list = [tuple(map(int, t.strip().split(","))) for t in f.readlines()]
    
    with open(f"{output_dir}/node_list.txt", "r") as f:
        node_list = [n.strip() for n in f.readlines()]

    named_list = [tuple(map(lambda x: node_list[x - 1], l)) for l in group_list]

    with open(f"{output_dir}/named_{target}.txt", "w") as f:
        print(*[",".join(l) for l in named_list], sep="\n", file=f)


def matrix_fix():
    target = "matrix_2021-01-01_2021-03-01.txt"
    with open(f"{output_dir}/{target}", "r") as f:
        matrix = [tuple(map(int, t.strip().split())) for t in f.readlines()]
    
    fixed = [tuple(x if i != j else 0 for j, x in enumerate(l)) for i, l in enumerate(matrix)]

    with open(f"{output_dir}/fixed_{target}", "w") as f:
        print(*[" ".join(map(str, l)) for l in fixed], sep="\n", file=f)


def hieralcy_join():
    with open(f"{output_dir}/sequence.txt", "r") as f:
        sequence = [tuple(map(int, l.strip().split())) for l in f.readlines()]

    # with open(f"{output_dir}/node_list.txt", "r") as f:
    #     node_list = [n.strip() for n in f.readlines()]

    G = []
    t = 0
    for s in sequence:
        t = max(t, s[0])
        a, b = s[1], s[-1]
        G2 = [tuple(s[1:])]
        for g in G:
            if a in g:
                continue
            if b in g:
                continue
            G2.append(g)
        G = G2
        
        print(f"{t / 1000} ({len(G)}): {G}")


def concat_clique():
    to_clique_id = [-1] * 5000
    target = "clique_2021-09-01_2021-11-01"
    with open(f"{output_dir}/{target}.txt", "r") as f:
        clique_list = [tuple(map(int, l.split())) for l in f.readlines()]
    
    next_id = 0
    for C in clique_list[::-1]:
        counter = {}
        for i in C:
            c = to_clique_id[i]
            if c == -1:
                continue
            counter[c] = counter.setdefault(c, 0) + 1

        if len(counter) == 0:
            for c in C:
                to_clique_id[c] = next_id
            next_id += 1
        elif len(counter) == 1:
            k, v = list(counter.items())[0]
            if v == len(C):
                continue
            if len(C) - v <= 2:
                for c in C:
                    to_clique_id[c] = k
            elif v <= 2:
                for c in C:
                    to_clique_id[c] = next_id
                next_id += 1
            else:
                print(f"ambient: {','.join(f'{k}: {v}' for k, v in counter.items())} : total {len(C)}")
        else:
            print(f"ambient: {','.join(f'{k}: {v}' for k, v in counter.items())} : total {len(C)}")
    
    clique_set = [set() for _ in range(next_id)]
    for i, c in enumerate(to_clique_id):
        if c == -1:
            continue
        clique_set[c].add(i)

    with open(f"{output_dir}/fixed_{target}.txt", "w") as f:
        for s in clique_set:
            print(",".join(map(str, s)), file=f)


def change_color():
    color_pallet = [
        "#E60012",
        "#F39800",
        "#FFF100",
        "#8FC31F",
        "#009944",
        "#009E96",
        "#00A0E9",
        "#0068B7",
        "#1D2088",
        "#920783",
        "#E4007F",
        "#E5004F",
        "#EF845C",
        "#F9C270",
        "#FFF67F",
        "#C1DB81",
        "#69BD83",
        "#61C1BE",
        "#54C3F1",
        "#6C9BD2",
        "#796BAF",
        "#BA79B1",
        "#EE87B4",
        "#EF858C",
    ]
    targets = [
        "2021-01-01_2021-03-01",
        "2021-03-01_2021-05-01",
        "2021-05-01_2021-07-01",
        "2021-07-01_2021-09-01",
        "2021-09-01_2021-11-01",
    ]
    static_group = 9

    for target in targets:
        print(target)
        to_clique = [-1] * 5000
        with open(f"{output_dir}/fixed_clique_{target}.txt", "r") as f:
            for c, s in enumerate(f.readlines()):
                if not s.strip():
                    continue
                for i in map(int, s.split(",")):
                    to_clique[i] = c 

        sn = "{http://graphml.graphdrawing.org/xmlns}"
        tree = ET.parse(f"{output_dir}/{target}.graphml")
        root = tree.getroot()
        graph = root.find(sn + "graph")
        # print(root[0].tag, root[0].attrib)
        # print(graph)
        nodes = graph.findall(sn + "node")
        # print(nodes[0].tag, nodes[0].attrib, nodes[0].get("id"))

        for node in nodes:
            node_id = int(node.find("./*[@key='d0']").text)
            c = to_clique[node_id]
            if c == -1:
                continue
            color_data = ET.SubElement(node, sn + "data")
            color_data.set("key", "d4")
            color_data.text = color_pallet[c]

            size_data = ET.SubElement(node, sn + "data")
            size_data.set("key", "d3")
            size_data.text = "7"
            if c >= static_group:
                node.find("./*[@key='d5']").text = "diamond"
                size_data.text = "5"
        tree.write(f"{output_dir}/fixed_{target}.graphml", encoding="utf-8")


if __name__ == "__main__":
    # make_friend_list()
    # target_id = chop_user_log()
    target_id = 2633
    connected_list_by(target_id)
    # put_name()
    output_wlist()
    # matrix_fix()
    # hieralcy_join()
    # concat_clique()
    # change_color()