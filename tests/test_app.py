'''
Test the app -- uses multiproccessing to avoid being blocking
'''

import sciris as sc
import multiprocessing as mp
from binomialbias import app as bbapp


def run_app():
    ''' Call the app to run programmatically '''
    bbapp.run()
    return


def test_app(delay=2):
    ''' Test that the app runs '''
    proc = mp.Process(target=run_app, args=())
    proc.start() # Starts app
    print(f'Waiting {delay} seconds before shutdown ...')
    sc.timedsleep(delay) # Waits for it to start
    proc.terminate() # Shuts down server
    return bbapp.app


if __name__ == '__main__':
    app = test_app()