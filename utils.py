from pathlib import Path
import json
import html

def extract_route(request):
    lista_palavras = request.split()
    relative_path = lista_palavras[1][1:]
    return relative_path  

def read_file(path: Path):
    with open(path,'rb') as file:
        return file.read()
def load_data(filename):
    data_dir = Path(__file__).parent / "data"
    filepath = data_dir / filename
    if not filepath.exists():
        return []
    try:
        return json.loads(filepath.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

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
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    filepath = data_dir / "notes.json"

    notas = load_data('notes.json')  # load_data já trata arquivo inexistente e JSON inválido
    notas.append(note)

    # grava usando Path
    filepath.write_text(json.dumps(notas, ensure_ascii=False, indent=4), encoding="utf-8")
    

