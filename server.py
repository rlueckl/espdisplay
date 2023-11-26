#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler

COUNTER_PATH = '/opt/espdisplay/counter.txt'

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def my_template(self, title, body):
        html = f'''<html lang="hu">
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
    </head>
    <body>
        {body}
    </body>
</html>'''
        return html

    def get_counter(self, path):
        with open(path, 'r') as myfile:
            counter = myfile.read()

        try:
            counter = int(counter)
        except ValueError:
            counter = 99999999

        return counter

    def do_GET(self):
        if self.path == '/update':
            counter = self.get_counter(COUNTER_PATH)

            if counter == 99999999:
                content = '<p>Hiba: a kiolvasott érték nem szám!</p>'
            else:
                content = f'<p>Számláló aktuális értéke: {counter}</p>'

            content += '''<p>
                <form action="/espdisp/cntupd" method="post">
                <label for="cntval">Új érték: </label><input type="number" id="cntval" name="cntval" />
                <input type="submit" value="Beállít" />
                <form>
            </p>'''

            html = self.my_template('Számláló frissítése', content)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(html.encode())

        elif self.path == '/numonly':
            counter = self.get_counter(COUNTER_PATH)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(counter).encode())

    def do_POST(self):
        if self.path == '/cntupd':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            counter_value = post_data.split("=")[1]

            with open(COUNTER_PATH, 'w') as myfile:
                myfile.write(counter_value)

            content = '''<p>Új érték beállítva</p>
            <p><a href="/espdisp/update">Vissza</a></p>'''

            html = self.my_template('Számláló frissítve', content)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(html.encode())

if __name__ == '__main__':
    httpd = HTTPServer(('127.0.0.1', 8080), SimpleHTTPRequestHandler)
    httpd.serve_forever()
