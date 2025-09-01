from urllib.parse import unquote_plus
from utils import (
    load_data,
    load_template,
    adiciona,
    build_response,
    toggle_favorite,
    delete_note,
    update_note,
    get_note_by_id,   # <- garantir que existe no utils.py com essa assinatura
)

# ----------------- Helpers internas -----------------

def parse_query_params(request: str) -> dict:
    """
    Extrai parâmetros de query (?a=1&b=2) da primeira linha do request GET.
    Retorna um dict como {'a': '1', 'b': '2'}.
    """
    first_line = request.split('\n', 1)[0]  # ex: "GET /?edit_id=123 HTTP/1.1"
    try:
        path = first_line.split(' ', 2)[1]  # "/?edit_id=123"
    except IndexError:
        return {}

    if '?' not in path:
        return {}

    query = path.split('?', 1)[1]          # "edit_id=123&x=y"
    params = {}
    for kv in query.split('&'):
        if not kv or '=' not in kv:
            continue
        k, v = kv.split('=', 1)
        params[k] = unquote_plus(v)
    return params


def html_escape(s: str) -> str:
    """
    Escape mínimo para injetar em value/textarea sem quebrar o HTML.
    """
    if s is None:
        return ''
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;'))


# ----------------- View principal -----------------

# ... imports permanecem (incluindo get_note_by_id, update_note) ...

def index(request: str) -> bytes:
    if request.startswith('POST'):
        request = request.replace('\r', '')
        header, body = (request.split('\n\n', 1) + [''])[:2]

        params = {}
        for kv in body.split('&'):
            if not kv or '=' not in kv:
                continue
            k, v = kv.split('=', 1)
            params[k] = unquote_plus(v)

        if 'favorite_id' in params and params['favorite_id'].isdigit():
            toggle_favorite(int(params['favorite_id']))
            return build_response(code=303, reason='See Other', headers='Location: /')

        if 'delete_id' in params and params['delete_id'].isdigit():
            delete_note(int(params['delete_id']))
            return build_response(code=303, reason='See Other', headers='Location: /')

        if 'update_id' in params and params['update_id'].isdigit():
            note_id  = int(params['update_id'])
            titulo   = params.get('titulo', '')
            detalhes = params.get('detalhes', '')
            tag      = params.get('tag', '') or ''
            update_note(note_id, titulo, detalhes, tag)
            return build_response(code=303, reason='See Other', headers='Location: /')

        # criar
        adiciona({
            'title'  : params.get('titulo')   or params.get('title')   or '',
            'content': params.get('detalhes') or params.get('content') or '',
            'tag'    : params.get('tag', '') or ''
        })
        return build_response(code=303, reason='See Other', headers='Location: /')

    # --- GET ---
    q = parse_query_params(request)
    edit_id = q.get('edit_id')

    if edit_id and edit_id.isdigit():
        n = get_note_by_id(int(edit_id))
        if n:
            form_title_value   = html_escape(n.get('title',''))
            form_details_value = html_escape(n.get('content',''))
            form_tag_value     = html_escape(n.get('tag',''))
            form_update_id     = str(n.get('id'))
            form_submit_label  = 'Atualizar'
            cancel_link        = '<a href="/" class="btn-cancel">Cancelar</a>'
        else:
            form_title_value = form_details_value = form_tag_value = ''
            form_update_id = ''
            form_submit_label = 'Criar'
            cancel_link = ''
    else:
        form_title_value = form_details_value = form_tag_value = ''
        form_update_id = ''
        form_submit_label = 'Criar'
        cancel_link = ''

    # cards
    note_template = load_template('components/note.html')
    cards_html = []
    for dados in load_data('notes.json'):
        fav_class = 'favorited' if dados.get('favorite') else ''
        cards_html.append(
            note_template.format(
                id=dados.get('id',''),
                title=dados.get('titulo','') or dados.get('title',''),
                details=dados.get('detalhes','') or dados.get('content','') or dados.get('details',''),
                tag=dados.get('tag','') or '',
                fav_class=fav_class
            )
        )
    notes = '\n'.join(cards_html)

    html = load_template('index.html').format(
        notes=notes,
        form_title_value=form_title_value,
        form_details_value=form_details_value,
        form_tag_value=form_tag_value,          # novo
        form_update_id=form_update_id,
        form_submit_label=form_submit_label,
        cancel_link=cancel_link
    )
    return build_response(html)
