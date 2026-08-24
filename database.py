import sqlite3
from logging import Logger


class Database:

    def __init__(self, path: str, logger: Logger) -> None:
        self.path: str = path
        self.logger: Logger = logger

    def create_table(self):
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            _ = cur.execute("CREATE TABLE IF NOT EXISTS images(num, id PRIMARY KEY, path, is_sended, purity)")
            cur.close()

    def add_to_database(self, num: int, id: str, url: str, rate: str):
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            _ = cur.execute("INSERT INTO images VALUES(?, ?, ?, ?, ?)", (num, id, url, False, rate))
            con.commit()

    def has_item(self, id: str) -> bool:
            with sqlite3.connect(self.path) as db:
                ids = db.execute("SELECT id FROM images")
                for db_id in ids.fetchall():
                    if db_id[0] == id:
                        self.logger.info("Такой элемент существует")
                        self.logger.info(db_id[0])
                        return True
                    else:
                        return False
                return False

    def is_sended(self, img_path: str) -> bool:
        with sqlite3.connect(self.path) as db:
            for db_photo in db.execute("SELECT path, is_sended FROM images"):
                if db_photo[0] == img_path:
                    return db_photo[1] == 1
            return False


    def get_last_id(self, purity: str) -> int:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            nums = cur.execute("SELECT num, purity FROM images ORDER BY num DESC")
            for num in nums:
                if num[1] == purity:
                    return num[0]
            return 1

    def mark_sended(self, path: str) -> None:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            paths = cur.execute("SELECT path FROM images")
            for db_path in paths.fetchall():
                if db_path[0] == path:
                    cur.execute("UPDATE images SET is_sended = ? WHERE path = ?", (1, path))
