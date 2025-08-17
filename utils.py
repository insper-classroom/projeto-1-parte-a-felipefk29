from pathlib import Path
import json

def extract_route(request):
    lista_palavras = request.split()
    relative_path = lista_palavras[1][1:]
    return relative_path  

def read_file(path: Path):
    with open(path,'rb') as file:
        return file.read()
    
def load_data(filename):
    with open(f"data/{filename}","r",encoding="utf-8") as f:
        dados = json.load(f)
    return dados
