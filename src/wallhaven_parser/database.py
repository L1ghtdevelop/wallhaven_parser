import sqlite3
from logging import Logger


class Database:

    def __init__(self, path: str, logger: Logger) -> None:
        """Initialize class database."""
        self.path: str = path
        self.logger: Logger = logger

    def create_table(self) -> None:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            _ = cur.execute(
"CREATE TABLE IF NOT EXISTS images(num, id, path, is_sended, purity)",
            )

    def delete_table(self) -> None:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            _ = cur.execute("DROP TABLE IF EXISTS images")

    def show_table(self) -> None:
        with sqlite3.connect(self.path) as db:
            cur = db.cursor()
            db_info = cur.execute("SELECT * FROM images")
            result:list[tuple[int, str, str, int, str]] = db_info.fetchall()
            for row in result:
                self.logger.info(row)

    def add_to_database(self, num: int, fid: str, url: str, rate: str) -> None:
        if not self.has_item(fid):
            self.logger.info("Enter to add func")
            with sqlite3.connect(self.path) as con:
                self.logger.info("Enter to contex")
                cur = con.cursor()
                _ = cur.execute("INSERT INTO images VALUES(?, ?, ?, ?, ?)",
                    (num, fid, url, 0, rate))
                con.commit()
                self.logger.info("Commited")
        else:
            self.logger.error("Такой элемент уже существует")

    def has_item(self, fid: str) -> bool:
            with sqlite3.connect(self.path) as db:
                ex = db.execute(
                    "SELECT id FROM images WHERE id = ?", (fid,))
                return bool(ex.fetchone())

    def is_sended(self, img_path: str) -> bool:
        with sqlite3.connect(self.path) as db:
            ex: sqlite3.Cursor = db.execute(
                "SELECT is_sended FROM images WHERE path = ?", (img_path,))
            is_sended = ex.fetchone()[0]
            return bool(is_sended) if is_sended else False

    def get_last_id(self, purity: str) -> int:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            db_nums = cur.execute(
            "SELECT num, purity FROM images WHERE purity = ? ORDER BY num DESC LIMIT 1",
                (purity,))
            return db_nums.fetchone()[0]

    def mark_sended(self, path: str) -> None:
        with sqlite3.connect(self.path) as con:
            cur = con.cursor()
            _ = cur.execute("UPDATE images SET is_sended = ? WHERE path = ?",
                (1, path))
