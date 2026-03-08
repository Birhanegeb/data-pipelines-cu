import sqlite3
db_path = "airflow_data/supermarket1/processed/supermarket.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM promotions")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
 
"""output of this query:
('P001', 2, '2026-03-08')
('P003', 1, '2026-03-08')
('P002', 1, '2026-03-08')"""