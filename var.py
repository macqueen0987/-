from json import loads
import requests
import json
import pymysql

games = None
parties = {}
shutdown = False
restart = False
temp_role_message = {}
role_message = {}
civil_party = {}
client = None


def init():
    global games
    with open("var.json", encoding='UTF-8') as jsonFile:
        Lines = jsonFile.readlines()
        jsonFile.close()


    jsonObjects = ''
    for Line in Lines:
        Line_process = Line.replace(" ","")
        if Line_process.startswith("//") or Line_process.startswith("\n"):
            pass
        else:
            jsonObjects += Line

    jsonObjects = loads(jsonObjects)

    for jsonObject in jsonObjects:
        globals()[jsonObject] = jsonObjects[jsonObject]

    r = requests.get("https://raw.githubusercontent.com/macqueen0987/Party-Bot/main/games.json")
    games = loads(r.text.replace("none", "null"))

    r = requests.get("https://raw.githubusercontent.com/macqueen0987/Party-Bot/main/var.json")
    jsonObjects = loads(r.text.replace("none", "null"))
    for jsonObject in jsonObjects:
        globals()[jsonObject] = jsonObjects[jsonObject]

    # get_role_messages()


# def get_role_messages():
#     global role_message
#     with open("roles.json") as jsonFile:
#         role_message = json.load(jsonFile)
#         jsonFile.close()


# def write_role_messages():
#     with open("roles.json", "w") as jsonFile:
#         json.dump(role_message, jsonFile)
#         jsonFile.close()


def db_conn():
    conn = pymysql.connect(host=host, user=user, password=password, database=database, cursorclass=pymysql.cursors.DictCursor, charset="utf8", port=9000)
    return conn


def db_disconn(conn):
    conn.cursor().close()
    conn.close()
    return


def db_query(conn, query):
    query = query
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    result = cur.fetchall()
    return result


def dumps(msg):
    msg = json.dumps(msg)
    msg = msg.replace("\\", "\\\\")
    msg = msg.replace("\'", "\\\'")
    msg = msg.replace("\"", "\\\"")
    return msg


if __name__ == '__main__':
    init()

