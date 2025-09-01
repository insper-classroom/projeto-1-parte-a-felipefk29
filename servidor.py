import socket
from pathlib import Path
from utils import read_file, extract_route, build_response, load_template
from views import index

CUR_DIR = Path(__file__).parent
SERVER_HOST = 'localhost'
SERVER_PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen()

print(f'Servidor escutando em (ctrl+click): http://{SERVER_HOST}:{SERVER_PORT}')

while True:
    client_connection, client_address = server_socket.accept()
    try:
        request = client_connection.recv(1024).decode()
        if not request:
            client_connection.close()
            continue

        print('*' * 100)
        print(request)

        route = extract_route(request)            # garante que remove ?query
        filepath = CUR_DIR / route

        if filepath.is_file():
            # arquivo estático (css/js/img etc.)
            response = build_response() + read_file(filepath)
        elif route == '':
            # rota raiz -> nossa view principal
            response = index(request)
        else:
            # 404 amigável
            body = load_template('404.html')      # templates/404.html
            response = build_response(body, code=404, reason='Not Found')

        # 🔻 Faltava isto:
        client_connection.sendall(response)

    except Exception as e:
        # Resposta 500 de emergência para facilitar o debug
        err_body = f"<h1>500 Internal Server Error</h1><pre>{e}</pre>"
        client_connection.sendall(
            build_response(err_body, code=500, reason='Internal Server Error')
        )
    finally:
        # 🔻 Feche a conexão a cada request
        client_connection.close()

server_socket.close()
