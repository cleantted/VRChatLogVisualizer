import configparser
import dao
import datetime
import heapq
import operator
import sys


def is_near_time(a_str, b_str):
    date_dt1 = datetime.datetime.strptime(a_str, "%Y-%m-%d %H:%M:%S")
    date_dt2 = datetime.datetime.strptime(b_str, "%Y-%m-%d %H:%M:%S")
    return (date_dt2 - date_dt1).seconds <= 1


def pickup(d, limit):
    L = sorted(list(d.items()), key=operator.itemgetter(1), reverse=True)[:limit]

    res = ""
    for i, (name, count) in enumerate(L):
        res += f"{name}[{count}], "
    return res


class Analyzer:
    __invalid_datetime = "9999-99-99 23:59:59"

    def __init__(self, orner_name, home_world):
        self.__dao = dao.VRChatActivityLogsDao()
        self.__orner_name = orner_name
        self.__home_world = home_world
        self.fetch_world_stay_time()
        self.fetch_players_in_world()
        self.fetch_players_relation()

    def fetch_world_stay_time(self):
        df = self.__dao.fetch_world_join_time()
        L = df.values.tolist()
        L.append(["", self.__invalid_datetime])

        world_data = [(
            L[i][0],
            L[i][1],
            L[i + 1][1],
        ) for i in range(len(L) - 1)]
        self.world_data = world_data

    def complete_player_data(self, players):
        buffer = {}
        player_data = []
        for user_name, timestamp, activity_type in players: 
            if activity_type == self.__dao.activity_type["met_player"]:
                if user_name in buffer:
                    print(f"[error] already added: {user_name} at {timestamp}", file=sys.stderr)
                    continue

                buffer[user_name] = timestamp
            elif activity_type == self.__dao.activity_type["leave_player"]:
                if user_name not in buffer:
                    print(f"[error] not exist: {user_name} at {timestamp}", file=sys.stderr)
                    continue
                player_data.append((buffer.pop(user_name), timestamp, user_name))
            else:
                print(f"[error] unknown type: {activity_type} of {user_name} at {timestamp}", file=sys.stderr)
        
        for user_name, timestamp in buffer.items():
            print(f"[warn] not left: {user_name} from {timestamp}", file=sys.stderr)
            player_data.append((timestamp, self.__invalid_datetime, user_name))
        player_data.sort()
        # print(player_data)
        return player_data

    def fetch_players_in_world(self):
        players = []
        for world_name, time_start, time_end in self.world_data:
            table = self.__dao.fetch_user_meet_data(time_start, time_end) 
            time_in_list = table[table["UserName"] == self.__orner_name]["Timestamp"].values.tolist()
            if not time_in_list:
                print(f"[error] not found {self.__orner_name} in world '{world_name}'\ntable: {table}", file=sys.stderr)
                continue
            time_in = time_in_list[0]
            users = self.complete_player_data(table.values.tolist())
            if not users:
                continue
            players.append((world_name, time_in, users))
        self.players = players

    def show_join_or_joined(self, players):
        meet_to_me = {}
        i_meet_who = {}
        for i, (world, time, pls) in enumerate(players):
            if world == self.__home_world:
                continue
            already_player = set(pl for pl, time_in, _ in pls if is_near_time(time, time_in))
            for pl in already_player:
                if pl == self.__orner_name:
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


    def fetch_players_relation(self):
        valid_player_data = filter(lambda x: x[2] != self.__invalid_datetime, self.players)
        relation = {self.__orner_name: dict()}
        for i, (world, time, pls) in enumerate(valid_player_data):
            queue = []
            joinning_player = {self.__orner_name}
            for in_time, out_time, pl in pls:
                if pl == self.__orner_name:
                    continue

                while queue and queue[0][0] < in_time:
                    joinning_player.remove(heapq.heappop(queue)[1])
                
                if is_near_time(time, in_time):
                    relation[self.__orner_name][pl] = relation[self.__orner_name].setdefault(pl, 0) + 1
                else:
                    for pl2 in joinning_player:
                        if pl2 == self.__orner_name:
                            continue
                        relation[pl][pl2] = relation.setdefault(pl, dict()).setdefault(pl2, 0) + 1

                heapq.heappush(queue, (out_time, pl))
                joinning_player.add(pl)
        
        for pl, to_join_list in relation.items():
            if max(to_join_list.values()) < 2:
                continue
            print(f"{pl}: {pickup(to_join_list, 5)}")
        # print(relation)
        self.relation = relation


if __name__ == "__main__":
    config_ini = configparser.ConfigParser()
    config_ini.read("./config.ini", encoding="utf-8")

    orner_name = config_ini["setting"]["orner_name"]
    home_world = config_ini["setting"]["home_world"]

    analyzer = Analyzer(orner_name, home_world)
    print(analyzer.relation)
