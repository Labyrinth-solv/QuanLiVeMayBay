import pymysql.cursors

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='17012005',
        db='pythonproject',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
