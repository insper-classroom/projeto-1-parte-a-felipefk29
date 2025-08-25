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

    def add(self, note):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO note (title, content) VALUES ('{note.title}','{note.content}')"
             )
        self.conn.commit()
    
    def get_all(self):
        notes = []
        cursor = self.conn.execute("SELECT id, title, content FROM note")

        for linha in cursor:
            _id = linha[0]
            titulo = linha[1]
            conteudo = linha[2]
            notes.append(Note(id = _id, title = titulo, content = conteudo))

        return notes
    
    def update(self, entry):
        cursor = self.conn.execute(f"UPDATE note SET title = '{entry.title}', content = '{entry.content}' WHERE id = '{entry.id}'")
        self.conn.commit()

    def delete(self,note_id):
        cursor = self.conn.execute(f"DELETE FROM note WHERE id = '{note_id}'")
        self.conn.commit()

class Note:

    def __init__(self, id=None, title=None, content=''):
        self.id = id
        self.title = title
        self.content = content


