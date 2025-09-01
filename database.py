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
        self.conn.commit()
        cols = [row[1] for row in cursor.execute("PRAGMA table_info(note)")]
        if 'favorite' not in cols:
            cursor.execute("ALTER TABLE note ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0;")
            self.conn.commit()

    def add(self, note):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO note (title, content, favorite) VALUES (?, ?, ?)",
            (note.title, note.content, getattr(note, 'favorite', 0))
        )
        self.conn.commit()
    
    def get_all(self):
        notes = []
        cursor = self.conn.execute("SELECT id, title, content, favorite FROM note ORDER BY favorite DESC, id DESC")
        for linha in cursor:
            _id, titulo, conteudo, fav = linha
            notes.append(Note(id=_id, title=titulo, content=conteudo, favorite=fav))
        return notes
    
    def update(self, entry):
        cursor = self.conn.execute(f"UPDATE note SET title = '{entry.title}', content = '{entry.content}' WHERE id = '{entry.id}'")
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
        cursor = self.conn.execute("SELECT id, title, content, favorite FROM note WHERE id = ?", 
                                  (note_id))
        row = cursor.fetchone() #Retira a primeira linha do resultado do SELECT armazenado na memória
        if row:             
            _id, titulo, conteudo, fav = row
            return Note(id=_id, title=titulo, content=conteudo, favorite=fav) #Caso exista a linha, retorna o objeto Note
        return None
    

class Note:

    def __init__(self, id=None, title=None, content='',favorite=0):
        self.id = id
        self.title = title
        self.content = content
        self.favorite = favorite


