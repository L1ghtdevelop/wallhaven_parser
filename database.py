import sqlite3


class Database:

    def __init__(self, path, logger) -> None:
        self.path = path
        self.logger = logger

    def create_table(self):
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS images(num, id, url, is_sended, path)")
            cur.close()

    def add_to_database(self, num, id, url, rate):
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO images VALUES(?, ?, ?, ?, ?)", (num, id, url, False, rate))
            con.commit()

    def has_item(self, id) -> bool:
            with sqlite3.connect(self.path) as db:
                ids = db.execute("SELECT id FROM images")
                for db_id in ids.fetchall():
                    self.logger.info(db_id[0])
                    self.logger.info(id)
                    if db_id[0] == id:
                        self.logger.info("Такой элемент существует")
                        self.logger.info(db_id)
                        return True
                else:
                    return False

    def get_last_id(self) -> int:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            nums = cur.execute("SELECT num FROM images ORDER BY num DESC")
            for num in nums:
                return num[0]
            return 1

