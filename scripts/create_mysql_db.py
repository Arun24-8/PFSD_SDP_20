import pymysql
import sys

host = 'root'
port_input = 'ok'
user = 'root'
password = 'admin'
db = 'ok'
app_user = 'ok'
app_pass = 'root'

try:
    port = int(port_input)
except Exception:
    port = 3306

print('Connecting to MySQL at', host, port, 'as', user)
try:
    conn = pymysql.connect(host=host, port=port, user=user,
                           password=password, autocommit=True)
    cur = conn.cursor()
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cur.execute(
        f"CREATE USER IF NOT EXISTS '{app_user}'@'%' IDENTIFIED BY %s;", (app_pass,))
    cur.execute(f"GRANT ALL PRIVILEGES ON `{db}`.* TO '{app_user}'@'%';")
    cur.execute('FLUSH PRIVILEGES;')
    print('Database and user created/ensured:', db, app_user)
    cur.close()
    conn.close()
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)
