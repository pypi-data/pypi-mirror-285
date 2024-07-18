import pg8000
from datetime import datetime


def booting(account):
    connect = pg8000.connect(host='139.196.89.94'
                             , port=5433
                             , user='allkey'
                             , password='_MERSB2p!FJ-j2S'
                             , database='db55a0dc67746c47419a375b86e34aec4fkey'
                             )
    try:
        with connect.cursor() as cursor:
            cursor.execute(F'''select deadline from booting_key where account = '{account}' ''')
            deadline_row = cursor.fetchone()
            cursor.execute("SELECT NOW()")
            current_time_row = cursor.fetchone()
            if deadline_row and current_time_row:
                deadline_obj = datetime.strptime(deadline_row[0], '%Y-%m-%d %H:%M:%S')
                deadline_timestamp = int(deadline_obj.timestamp())
                current_time_timestamp = current_time_row[0].timestamp()
                return deadline_timestamp - current_time_timestamp
        cursor.close()
    except Exception as error:
        print(error)
    finally:
        connect.close()
