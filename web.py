from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)


@app.route("/get")
def save():
    # here we want to get the value of user (i.e. ?user=some-value)
    image_url = request.args.get('url')
    db = Database('local.db.sqlite3')
    db.add_image(image_url)
    return "image_url: {0}".format(image_url)

@app.route("/")
def show():

    page = ''
    page += '<script type="text/javascript" src="//api.filepicker.io/v1/filepicker.js"></script>'
    page += '<script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>'
    page += '<script>'
    page += 'function onFinish(image_url) {'
    page += '    $.get( "/get", { url: image_url } ).done('
    page += '        location.reload()'
    page += '    )'
    page += '}'
    page += '</script>'
    page += '<input type="filepicker" data-fp-apikey="{0}" data-fp-mimetypes="image/*" data-fp-container="modal" ' \
            'onchange="onFinish(event.fpfile.url)">'.format(os.environ['FILEPICKER_API_KEY'])
    page += '<br />'

    db = Database('local.db.sqlite3')
    page += '<table>'
    for row in db.get_images():
        page += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td><img src="{3}" height="64" width="64">' \
                '</td><td><img src="{3}/convert?crop=3,3,13,13"></td></tr>'.format(row[0], row[1], row[2], row[1])
    page += '</table>'
    return page


class Database(object):

    def __init__(self, db_file_path):
        self.conn = sqlite3.connect(db_file_path)
        #create table if doesn't exists
        self.create_table()

    def create_table(self):
        c = self.conn.cursor()
        create_db = """
            CREATE TABLE IF NOT EXISTS Images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                created DATETIME DEFAULT current_timestamp
            );
            """
        c.execute(create_db)
        self.conn.commit()

    def add_image(self, image):
        c = self.conn.cursor()
        query = "INSERT INTO Images (url) values (?);"
        c.execute(query, [image])
        self.conn.commit()

    def get_images(self):
        c = self.conn.cursor()
        query = "SELECT * FROM Images order by id;"
        return c.execute(query)

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    app.debug = True
    app.run(port=5001, host='192.168.33.13')

