import sqlite3
import pandas as ps


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
                select {self.__column_name["user_name"]}, count(*) 
                from {self.__table_name} 
                where {self.__column_name["activity_type"]} = 1
                group by {self.__column_name["user_name"]}
                order by 2 desc
                limit {limit}
            """, self.conn)
        return df

    def fetch_world_join_time(self):
        df = ps.read_sql(f"""
            select
                {self.__column_name["world_name"]},
                {self.__column_name["timestamp"]}
            from {self.__table_name}
            where
                {self.__column_name["activity_type"]} = 0
        """, self.conn)
        return df 

    def fetch_user_meet_data(self, time_start, time_end): 
        df = ps.read_sql(f"""
            select 
                {self.__column_name["user_name"]},
                {self.__column_name["timestamp"]}
            from {self.__table_name}
            where
                {self.__column_name["activity_type"]} = 1
                and {self.__column_name["timestamp"]} 
                    between '{time_start}' and '{time_end}'
        """, self.conn)
        return df

    def query(self, query):
        return ps.read_sql(query, self.conn)


if __name__ == "__main__":
    dao = VRChatActivityLogsDao()
    print(dao.meets_counts())