import dao
import datetime


def is_near_time(a_str, b_str):
    date_dt1 = datetime.datetime.strptime(a_str, "%Y-%m-%d %H:%M:%S")
    date_dt2 = datetime.datetime.strptime(b_str, "%Y-%m-%d %H:%M:%S")
    return (date_dt2 - date_dt1).seconds <= 1


def world_join_status():
    activity_logs_dao = dao.VRChatActivityLogsDao()
    df = activity_logs_dao.fetch_world_join_time()
    L = df.values.tolist()
    L.append(["", "9999-99-99 23:59:59"])

    world_data = [(
        L[i][0],
        L[i][1],
        L[i + 1][1],
    ) for i in range(len(L) - 1)]

    players = []
    for world_name, time_start, time_end in world_data:
        table = activity_logs_dao.fetch_user_meet_data(time_start, time_end) 
        time_in_list = table[table["UserName"] == "cleantted"]["Timestamp"].values.tolist()
        if not time_in_list:
            print(f"not fount cleantted in world '{world_name}'\ntable: {table}")
            continue
        time_in = time_in_list[0]
        users = table.values.tolist()
        if not users:
            continue
        players.append((world_name, time_in, users))
    # print(players)

    for i, (world, time, pls) in enumerate(players):
        if world == "VRChat Home":
            continue
        already_count = len(set(pl for pl, time_in in pls if is_near_time(time, time_in))) - 1
        comming_count = len(set(pl for pl, _ in pls)) - already_count - 1
        assert(already_count >= 0 and comming_count >= 0)
        print(f"[{i}] {world}: すでにいた人: {already_count}人, 入ってきた人: {comming_count}人")


if __name__ == "__main__":
    world_join_status()

