from pathlib import Path
import json
from database import Database, Note

def extract_route(request: str) -> str:
    """
    Extrai a rota do primeiro cabeçalho HTTP. Retorna string vazia se não conseguir.
    """
    if not request:
        return ''
    lines = request.splitlines()
    if not lines:
        return ''
    first = lines[0].strip()
    if not first:
        return ''
    parts = first.split()
    if len(parts) < 2:
        return ''
    path = parts[1]
    if path.startswith('/'):
        path = path[1:]
    if '?' in path:               # remove ?edit_id=...
        path = path.split('?', 1)[0]
    return path

def read_file(path: Path):
    with open(path,'rb') as file:
        return file.read()
    
def load_data(filename):
    if filename == 'notes.json':
        db = Database('notes')
        notes = db.get_all()
        return [
            {
                'id': n.id,
                'title': n.title,
                'content': n.content,
                'favorite': getattr(n, 'favorite', 0),
                'tag': getattr(n, 'tag', '') or ''
            } for n in notes
        ]
    return []
# def load_data(filename):
#     if filename == 'notes.json':
#         # use 'notes' (Database adiciona .db internamente) — igual ao usado em adiciona()
#         db = Database('notes')
#         notes = db.get_all()
#         # retornar as chaves que a aplicação espera: 'id', 'title', 'content'
#         return [{'id': note.id, 'title': note.title, 'content': note.content, 'favorite': getattr(note,'favorite',0)} for note in notes]

#     data_dir = Path(__file__).parent / "data"
#     filepath = data_dir / filename
#     if not filepath.exists():
#         return []
#     try:
#         return json.loads(filepath.read_text(encoding="utf-8"))
#     except json.JSONDecodeError:
#         return []

def load_template(filename):
    templates_dir = Path(__file__).parent / "templates"
    filepath = templates_dir / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Template not found: {filepath}")
    return filepath.read_text(encoding="utf-8")

def build_response(body='', code=200, reason='OK', headers=''):
    response_line = f'HTTP/1.1 {code} {reason}\n'
    if headers:
        response_headers = headers + '\n'
    else:
        response_headers = ''
    blank_line = '\n'
    response = response_line + response_headers + blank_line + body
    return response.encode()

def adiciona(note):
    db = Database('notes')
    if isinstance(note, dict):
        title = note.get('title')
        content = note.get('content', '')
        favorite = int(note.get('favorite', 0))
        tag = note.get('tag', '') or ''
        note_obj = Note(title=title, content=content, favorite=favorite, tag=tag)
    elif isinstance(note, Note):
        note_obj = note
    else:
        note_obj = Note(title=None, content=str(note), favorite=0, tag='')
    db.add(note_obj)


def toggle_favorite(note_id: int):
    db = Database('notes')
    db.toggle_favorite(note_id)

def delete_note(note_id: int):
    db = Database('notes')
    db.delete(note_id)

def get_note_by_id(note_id: int):
    db = Database('notes')
    n = db.get_by_id(note_id)
    if not n:
        return None
    return {'id': n.id, 'title': n.title or '', 'content': n.content or '',
            'favorite': getattr(n, 'favorite', 0), 'tag': getattr(n, 'tag', '') or ''}

def update_note(note_id: int, title: str, content: str, tag: str):
    db = Database('notes')
    entry = Note(id=note_id, title=title, content=content, tag=tag or '')
    db.update(entry)
