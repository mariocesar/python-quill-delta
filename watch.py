#!/usr/bin/env python
import sys
import logging
import pathlib
import subprocess
import time

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

root = pathlib.Path(__file__).parent.resolve()

command = ['pytest', 'tests/']

if len(sys.argv) > 0:
    tail = command.pop()
    command.extend(sys.argv[1:])
    command.append(tail)


class EventHandler(PatternMatchingEventHandler):
    def process(self, event):
        logging.info(f'Running {" ".join(command)}')

        process = subprocess.Popen(' '.join(command), shell=True)
        process.wait()

    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')


    event_handler = EventHandler(
        patterns=['*.py'],
        ignore_directories=True,
    )

    observer = Observer()
    observer.schedule(event_handler, f'{root}/tests', recursive=True)
    observer.schedule(event_handler, f'{root}/quilldelta', recursive=True)
    observer.start()

    logging.info('Start watching changes')
    logging.info(f'Running command {" ".join(command)}')

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
