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

    def delete_table(self):
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            _ = cur.execute("DROP TABLE IF EXISTS images")
            cur.close()

    def show_table(self):
        with sqlite3.connect(self.path) as db:
            cur = db.cursor()
            db_info = cur.execute("SELECT * FROM images")
            result:list[tuple[int, str, str, int, str]] = db_info.fetchall()
            for row in result:
                print(row)
                self.logger.info(row)

    def add_to_database(self, num: int, id: str, url: str, rate: str):
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            _ = cur.execute("INSERT INTO images VALUES(?, ?, ?, ?, ?)", (num, id, url, False, rate))
            con.commit()
            cur.close()

    def has_item(self, id: str) -> bool:
            with sqlite3.connect(self.path) as db:
                db_ids: sqlite3.Cursor = db.execute("SELECT id FROM images")
                ids: list[str] = db_ids.fetchall()
                for db_id in ids:
                    if db_id[0] == id:
                        self.logger.info("Такой элемент существует")
                        self.logger.info(db_id[0])
                        return True
                    else:
                        return False
                return False

    def is_sended(self, img_path: str) -> bool:
        with sqlite3.connect(self.path) as db:
            db_photo: sqlite3.Cursor = db.execute("SELECT path, is_sended FROM images")
            photo_info:list[tuple[str, int]] = db_photo.fetchall()
            for info in photo_info:
                if info[0] == img_path:
                    return info[1] == 1
            return False

    def get_last_id(self, purity: str) -> int:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            db_nums = cur.execute("SELECT num, purity FROM images ORDER BY num DESC")
            nums: list[tuple[int, str]] = db_nums.fetchall()
            for num in nums:
                if num[1] == purity:
                    cur.close()
                    return num[0]
            cur.close()
            return 1

    def mark_sended(self, path: str) -> None:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            db_paths = cur.execute("SELECT path FROM images")
            paths: list[str] = db_paths.fetchall()
            for old_path in paths:
                if old_path[0] == path:
                    _ = cur.execute("UPDATE images SET is_sended = ? WHERE path = ?", (1, path))
