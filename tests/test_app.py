'''
Test the app -- uses threads to avoid being blocking
'''

import threading
import binomialbias as bb


def run_app():
    bb.app.run()
    return

def test_app(delay=2):
    thread = threading.Thread(target=run_app)
    thread.start()
    # thread.join(delay)
    # bb.app.app.stop()
    return bb.app.app

if __name__ == '__main__':
    app = test_app()

    