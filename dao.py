import sqlite3
import pandas as ps
from enum import IntEnum


class ActivityType(IntEnum):
    JOIN_ROOM = 0
    MET_PLAYER = 1
    SEND_INVITE = 2
    RECEVED_INVITE = 3
    SEND_REQUEST_INVITE = 4
    RECEIVED_REQUEST_INVITE = 5
    SEND_FRIEND_REQUEST = 6
    RECEIVED_FRIEND_REQUEST = 7
    ACCEPT_FRIEND_REQUEST = 8
    LEAVE_PLAYER = 9


class VRChatActivityLogsDao:
    __table_name = "ActivityLogs"
    __column_name = {
        "id": "ID", 
        "activity_type": "ActivityType", 
        "timestamp": "Timestamp", 
        "notificaton_id": "NotificationID", 
        "user_id": "UserID", 
        "user_name": "UserName", 
        "world_id": "WorldID", 
        "world_name": "WorldName",
    }

    def __init__(self, db_name="./VRChatActivityLog.db"):
        self.conn = sqlite3.connect(db_name)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def meets_counts(self, limit=20):
        df = ps.read_sql(
            f"""
                select 
                    {self.__column_name["user_name"]}, 
                    count(*) 
                from {self.__table_name} 
                where {self.__column_name["activity_type"]} 
                        = {int(ActivityType.MET_PLAYER)}
                group by {self.__column_name["user_name"]}
                order by 2 desc
                limit {limit}
            """, self.conn)
        return df

    def fetch_world_join_time(self):
        df = ps.read_sql(
            f"""
                select
                    {self.__column_name["world_name"]},
                    {self.__column_name["timestamp"]}
                from {self.__table_name}
                where
                    {self.__column_name["activity_type"]} 
                        = {int(ActivityType.JOIN_ROOM)} 
                order by {self.__column_name["timestamp"]} asc
            """, self.conn)
        return df 

    def fetch_user_meet_data(self, time_start, time_end): 
        df = ps.read_sql(
            f"""
                select 
                    {self.__column_name["user_name"]},
                    {self.__column_name["timestamp"]},
                    {self.__column_name["activity_type"]}
                from {self.__table_name}
                where
                    {self.__column_name["activity_type"]} 
                        in ({int(ActivityType.MET_PLAYER)},
                            {int(ActivityType.LEAVE_PLAYER)})
                    and {self.__column_name["timestamp"]} 
                        between '{time_start}' and '{time_end}'
                order by {self.__column_name["timestamp"]} asc
            """, self.conn)
        return df

    def query(self, query):
        return ps.read_sql(query, self.conn)


if __name__ == "__main__":
    dao = VRChatActivityLogsDao()
    print(dao.meets_counts())