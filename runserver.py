"""
This script runs the w48687_wzorce_projektowe application using a development server.
"""
from __future__ import annotations
from typing import Any, List
from os import environ
from w48687_wzorce_projektowe import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
