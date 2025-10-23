import sqlite3, json, os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db.sqlite3")
con = sqlite3.connect(DB)
cur = con.cursor()

def cols(table):
    cur.execute(f'PRAGMA table_info({table})')
    return [r[1] for r in cur.fetchall()]

for t in ["complaints_complaint", "complaints_historicalcomplaint"]:
    try:
        print(t, json.dumps(cols(t)))
    except Exception as e:
        print(t, "error:", e)
con.close()
