import os
import sys
# Ensure parent workspace is on sys.path so `from Itihaas import create_app` works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Itihaas import create_app


def main():
    app = create_app()
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
