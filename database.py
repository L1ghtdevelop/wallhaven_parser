import sqlite3

class Database:

    def __init__(self, path, logger) -> None:
        self.path = path
        self.logger = logger

    def create_table(self):
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS images(num, id PRIMARY KEY, path, is_sended, purity)")
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
                    if db_id[0] == id:
                        self.logger.info("Такой элемент существует")
                        self.logger.info(db_id[0])
                        return True
                else:
                    return False

    def is_sended(self, img_path):
        with sqlite3.connect(self.path) as db:
            for db_photo in db.execute("SELECT path, is_sended FROM images"):
                if db_photo[0] == img_path:
                    if db_photo[1] == 1:
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

    def mark_sended(self, path):
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            paths = cur.execute("SELECT path FROM images")
            for db_path in paths.fetchall():
                if db_path[0] == path:
                    cur.execute("UPDATE images SET is_sended = ? WHERE path = ?", (1, path))


