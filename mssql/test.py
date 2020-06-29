import pymssql

conn = pymssql.connect('192.168.0.101', 'Administrator', '1994', 'JALiFactory')

cur = conn.cursor()

sql = 'select * from dbo.J_ALiIdMacP2p'


cur.execute(sql)

row = cur.fetchone()

print(row)
