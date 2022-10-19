import datetime
import sqlite3

db_path = '../dsmr50.1.sqlite'
# f'{item[1]:.2f}'
def get_returning(today=True):
    raw_d = {}
    data = []

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    if today:
        now = str(datetime.date.today())
        cur.execute(f"SELECT created_at, actual_returning FROM electric WHERE created_at BETWEEN '{now} 00:00:00' AND '{now} 23:59:59'")
    else:
        cur.execute(
            f"SELECT created_at, actual_returning FROM electric")
    for k, v in cur.fetchall():
        k = k.split(' ')[1][:2] # we only want the hour for our graph label
        if k not in raw_d.keys():
            raw_d[k] = [(k, v)]
        else:
            raw_d[k].append(('.', v))

    for k in sorted(raw_d):
        data += raw_d[k]
    return data

if __name__ == '__main__':
    print(get_returning())