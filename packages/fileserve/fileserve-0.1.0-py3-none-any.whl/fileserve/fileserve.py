import click
import http.server
import socketserver
import base64
import logging
import ssl


@click.command()
@click.option("--bind", default="localhost:8000", help="Host and port to bind to")
@click.option("--directory", default="/", help="Directory to serve files from")
@click.option("--auth", is_flag=True, help="Enable authentication")
@click.option("--log", is_flag=True, help="Enable logging")
@click.option("--https", is_flag=True, help="Enable HTTPS")
def serve_files(bind, directory, auth, log, https):
    Handler = http.server.SimpleHTTPRequestHandler

    if auth:
        username = input("Enter username: ")
        password = input("Enter password: ")
        credentials = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode(
            "utf-8"
        )
        Handler = get_auth_handler(credentials, Handler)

    if log:
        logging.basicConfig(filename="server.log", level=logging.INFO)

    if https:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")
        host, port = bind.split(":")
        httpd = socketserver.TCPServer((host, port), Handler)
        httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)
    else:
        host, port = bind.split(":")
        httpd = socketserver.TCPServer((host, port), Handler)

    click.echo(f"Server started at {host}:{port}")
    click.echo(f"Serving files from {directory}")
    if auth:
        click.echo("Authentication enabled")
    if log:
        click.echo("Logging enabled")
    if https:
        click.echo("HTTPS enabled")
    httpd.serve_forever()


def get_auth_handler(credentials, handler):
    class AuthHandler(handler):
        def handle_one_request(self):
            self.authenticate()
            super().handle_one_request()

        def authenticate(self):
            self.send_response(401)
            self.send_header(
                "WWW-Authenticate", 'Basic realm="Authentication required"'
            )
            self.end_headers()
            auth_header = self.headers.get("Authorization")
            if auth_header:
                encoded_credentials = auth_header.split(" ")[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode(
                    "utf-8"
                )
                if decoded_credentials == credentials:
                    return
            self.send_error(401, "Authentication failed")

    return AuthHandler


if __name__ == "__main__":
    serve_files()
