import sqlite3
from dataclasses import dataclass

class Database():
    def __init__(self,db_name):
        if not db_name.endswith(".db"):  #Checa se o arquivo esta no formato de data base
            db_name += ".db" # Se não estiver no formato adequado, ele corrige
        self.conn = sqlite3.connect(db_name)

        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()  # Cria um cursor, um objeto intermediário para comunicação com o SQL
        #execute: recebe uma string contendo um comando SQL e envia para o banco de dados:
        cursor.execute(""" CREATE TABLE IF NOT EXISTS note(  
                    id INTEGER PRIMARY KEY, 
                    title TEXT,
                     content TEXT NOT NULL 
                     );
                     """)
        cols = [row[1] for row in cursor.execute("PRAGMA table_info(note)")]
        if 'favorite' not in cols:
            cursor.execute("ALTER TABLE note ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0;")
            self.conn.commit()
        if 'tag' not in cols:
            cursor.execute("ALTER TABLE note ADD COLUMN tag TEXT DEFAULT '';")
            self.conn.commit()
        

    def add(self, note):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO note (title, content, favorite, tag) VALUES (?, ?, ?, ?)",
            (note.title, note.content, getattr(note, 'favorite', 0), getattr(note, 'tag', '') or '')
        )
        self.conn.commit()
    
    def get_all(self):
        notes = []
        cursor = self.conn.execute(
            "SELECT id, title, content, favorite, tag FROM note ORDER BY favorite DESC, id DESC"
        )
        for _id, titulo, conteudo, fav, tag in cursor:
            notes.append(Note(id=_id, title=titulo, content=conteudo, favorite=fav, tag=tag or ''))
        return notes
        
    def update(self, entry):
        # se não vier tag no entry, mantém a do banco
        tag = getattr(entry, 'tag', None)
        if tag is None:
            current = self.get_by_id(entry.id)
            tag = current.tag if current else ''
        self.conn.execute(
            "UPDATE note SET title = ?, content = ?, tag = ? WHERE id = ?",
            (entry.title, entry.content, tag, entry.id)
        )
        self.conn.commit()

    def delete(self,note_id):
        cursor = self.conn.execute(f"DELETE FROM note WHERE id = '{note_id}'")
        self.conn.commit()
    def toggle_favorite(self, note_id):
        # inverte 0<->1 de forma segura
        self.conn.execute(
            "UPDATE note SET favorite = CASE favorite WHEN 1 THEN 0 ELSE 1 END WHERE id = ?",
            (note_id,)
        )
        self.conn.commit()
    def get_by_id(self, note_id):
        try:
            note_id = int(note_id)
        except (TypeError, ValueError):
            return None
        cursor = self.conn.execute(
            "SELECT id, title, content, favorite, tag FROM note WHERE id = ?",
            (note_id,)   # tupla de 1 elemento!
        )
        row = cursor.fetchone()
        if row:
            _id, titulo, conteudo, fav, tag = row
            return Note(id=_id, title=titulo, content=conteudo, favorite=fav, tag=tag or '')
        return None
    

class Note:

    def __init__(self, id=None, title=None, content='',favorite=0, tag=None):
        self.id = id
        self.title = title
        self.content = content
        self.favorite = favorite
        self.tag = tag or ''

