#! /usr/bin/env python3
import os
import app
import flask_script
import flask_httpauth

app = app.create_app(os.getenv('FLASK_CONFIG'))
manager = flask_script.Manager(app)


def make_shell_context():
    return dict(app=app, db=app.db)
manager.add_command("shell", flask_script.Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
