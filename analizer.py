import dao
import datetime
import operator


def is_near_time(a_str, b_str):
    date_dt1 = datetime.datetime.strptime(a_str, "%Y-%m-%d %H:%M:%S")
    date_dt2 = datetime.datetime.strptime(b_str, "%Y-%m-%d %H:%M:%S")
    return (date_dt2 - date_dt1).seconds <= 1


def fetch_world_stay_time(dao):
    df = dao.fetch_world_join_time()
    L = df.values.tolist()
    L.append(["", "9999-99-99 23:59:59"])

    world_data = [(
        L[i][0],
        L[i][1],
        L[i + 1][1],
    ) for i in range(len(L) - 1)]

    return world_data


def fetch_players_in_world(dao, world_data):
    players = []
    for world_name, time_start, time_end in world_data:
        table = dao.fetch_user_meet_data(time_start, time_end) 
        time_in_list = table[table["UserName"] == "cleantted"]["Timestamp"].values.tolist()
        if not time_in_list:
            print(f"not fount cleantted in world '{world_name}'\ntable: {table}")
            continue
        time_in = time_in_list[0]
        users = complete_player_data(table.values.tolist())
        if not users:
            continue
        players.append((world_name, time_in, users))
    return players


def show_join_or_joined(players):
    meet_to_me = {}
    i_meet_who = {}
    for i, (world, time, pls) in enumerate(players):
        if world == "VRChat Home":
            continue
        already_player = set(pl for pl, time_in, _ in pls if is_near_time(time, time_in))
        for pl in already_player:
            if pl == "cleantted":
                continue
            i_meet_who[pl] = i_meet_who.setdefault(pl, 0) + 1

        comming_player = set(pl for pl, time_in, _ in pls if not is_near_time(time, time_in))
        for pl in comming_player:
            meet_to_me[pl] = meet_to_me.setdefault(pl, 0) + 1

        already_count = len(already_player) - 1
        comming_count = len(comming_player)
        assert(already_count >= 0 and comming_count >= 0)
        # print(f"[{i}] {world}: すでにいた人: {already_count}人, 入ってきた人: {comming_count}人")

    S1 = sorted(list(i_meet_who.items()), key=operator.itemgetter(1), reverse=True)
    S2 = sorted(list(meet_to_me.items()), key=operator.itemgetter(1), reverse=True)

    print("I meet to: ")
    for i in range(10):
        print(f"[{i + 1}] {S1[i][0]}: {S1[i][1]}回")

    print("")
    print("who meet to me(?): ")
    for i in range(10):
        print(f"[{i + 1}] {S2[i][0]}: {S2[i][1]}回")


if __name__ == "__main__":
    activity_logs_dao = dao.VRChatActivityLogsDao()
    world_data = fetch_world_stay_time(activity_logs_dao)
    players = fetch_players_in_world(activity_logs_dao, world_data)
    show_join_or_joined(players)
