from twJTools.Jasper_db_postgres import DBConnect

if __name__ == '__main__':
    db = DBConnect(printlog=True)
    try:
        db.execute("SELECT 1")
    finally:
        db.close()
