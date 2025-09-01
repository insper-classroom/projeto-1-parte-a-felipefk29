from utils import load_data, load_template, adiciona, build_response, toggle_favorite
from urllib.parse import unquote_plus

def index(request):
    if request.startswith('POST'):
        request = request.replace('\r', '')
        partes = request.split('\n\n')
        corpo = partes[1] if len(partes) > 1 else ''
        params = {}
        for chave_valor in corpo.split('&'):
            if not chave_valor:
                continue
            chave, valor = chave_valor.split("=", 1)
            params[chave] = unquote_plus(valor)

        # Ramo 1: toggle de favorito
        if 'favorite_id' in params and params['favorite_id'].isdigit():
            toggle_favorite(int(params['favorite_id']))
            return build_response(code=303, reason='See Other', headers='Location: /')

        # Ramo 2: criação de nota
        adiciona({
            'title': params.get('titulo') or params.get('title') or '',
            'content': params.get('detalhes') or params.get('content') or '',
        })
        return build_response(code=303, reason='See Other', headers='Location: /')

    note_template = load_template('components/note.html')
    notes_li = []
    for dados in load_data('notes.json'):
        fav_class = 'favorited' if dados.get('favorite') else ''
        notes_li.append(
            note_template.format(
                id=dados.get('id', ''),
                title=dados.get('titulo', '') or dados.get('title', ''),
                details=dados.get('detalhes', '') or dados.get('content', '') or dados.get('details', ''),
                fav_class=fav_class
            )
        )
    notes = '\n'.join(notes_li)
    return build_response(load_template('index.html').format(notes=notes))