import sqlite3
import pandas as pd

class Database():
  def __init__(self, path):
    self.conn = sqlite3.connect(path)
    cs = self.conn.cursor()
    self._create_table(cs)
  def _create_table(self, cs):
    cs.execute('''
      CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        /* info */
        date DATE NOT NULL,
        author TEXT NOT NULL,
        job TEXT NOT NULL,
        content TEXT NOT NULL,
        url TEXT NULL,
        label TEXT NULL,
        topic INTEGER NULL,
        /* plot */
        x REAL NOT NULL,
        y REAL NOT NULL
      );
    ''')
    self.conn.commit()
  def _truncate(self, cs):
    cs.execute('DELETE FROM comments')
  def _append(self, cs, df):
    cs.executemany('''
      INSERT INTO comments (date, author, job, content, url, label, topic, x, y)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', df.fillna('').apply(
      lambda r: list(map(lambda x: r[x],
        ('date', 'name', 'job', 'comment', 'url', 'label', 'topic', 'x', 'y'))),
      axis=1
    ).values)
  def _save(self, cs, df):
    cs.executemany('''
      INSERT INTO comments (id, date, author, job, content, url, label, topic, x, y)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(id) DO UPDATE SET
        id=id, date=date, author=author, job=job, content=content, url=url, x=x, y=y
    ''', df.fillna('').apply(
      lambda r: list(map(lambda x: r[x],
        ('id', 'date', 'name', 'job', 'comment', 'url', 'label', 'topic', 'x', 'y'))),
        axis=1
    ).values)
  def truncate(self):
    cs = self.conn.cursor()
    self._truncate(cs)
    self.conn.commit()
  def append(self, df):
    cs = self.conn.cursor()
    self._append(cs, df)
    self.conn.commit()
  def replace_all(self, df):
    cs = self.conn.cursor()
    self._truncate(cs)
    self._append(cs, df)
    self.conn.commit()
  def save(self, df):
    cs = self.conn.cursor()
    self._save(cs, df)
    self.conn.commit()
  def fetchall(self):
    cs = self.conn.cursor()
    rows = cs.execute('''
      SELECT id, date, author, job, label, content, url, topic, x, y FROM comments
    ''').fetchall()
    return pd.DataFrame(
      rows, columns=('id', 'date', 'name', 'job', 'label', 'comment', 'url', 'topic', 'x', 'y'))
  def __del__(self):
    self.conn.close()
