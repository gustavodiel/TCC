#!/usr/local/bin/python3

from pathlib import Path
import time
import argparse
import threading


class Watcher(threading.Thread):

    def __init__(self, file_name):
        threading.Thread.__init__(self)

        self.curr_file_size = 0
        self.prev_file_size = 0
        self.equals_counter = 0

        self.should_stop = False

        self.scan_file = Path(file_name)
        if self.scan_file.exists():
            self.scan_file.unlink()

    def run(self):
        while True:
            time.sleep(0.05)
            if not self.scan_file.exists():
                print("ERROR: File {} does not exist!".format(self.scan_file.name))
                continue
            else:
                print("File {} found! Starting to watch it".format(self.scan_file.name))
                break

        start_time = time.time()
        while not self.should_stop:
            time.sleep(0.25)

            self.prev_file_size = self.curr_file_size
            self.curr_file_size = self.scan_file.stat().st_size

            if self.prev_file_size == self.curr_file_size:
                self.equals_counter += 1
                if self.equals_counter >= 3:
                    print("Done! Files have stopped being modified")
                    self.should_stop = True
            else:
                self.equals_counter = 0

        end_time = time.time()

        print("Took {} seconds for file {} to complete the transfer".format(end_time - start_time, self.scan_file.name))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Execute a watcher for one or more files.')
    parser.add_argument('files', metavar='file', type=str, nargs='+',
                        help='Files the script will watch for modifications.')

    args = parser.parse_args()

    threads = []
    try:
        for file in args.files:
            thread = Watcher(file)
            threads.append(thread)
            thread.start()
    except RuntimeError:
        print("ERROR: Failed to execute thread!")

    for thread in threads:
        thread.join()

