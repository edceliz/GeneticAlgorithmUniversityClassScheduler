from components import Database as db

if __name__ == '__main__':
    conn = db.getConnection()
    cursor = conn.cursor()
    cursor.commit()
    conn.close()