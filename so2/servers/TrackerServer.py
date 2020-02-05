# -*- coding: utf-8 -*-

import logging
from multiprocessing import Process, Queue

import gevent

from sledilnik.TrackerGame import Tracker
from so2.servers.Server import Server


class TrackerServer(Server):
    """Tracker process babysitter

    Server spawns an external OpenCV tracker process and reads data from it.

    """

    def __init__(self):
        Server.__init__(self)

        self.logger = logging.getLogger('sledenje-objektom.TrackerServer')

        self.state = None
        self.queue = Queue()

        self.tracker = Tracker()
        self.tracker.setDebug()
        self.tracker.setVideoSource('./so2/tracker/ROBO_3.mp4')

        self.p = Process(target=self.tracker.start, args=(self.queue,))

    def _run(self):
        # Start tracker in another process and open message queue
        self.p.start()
        self.logger.info("Tracker server started.")

        while True:
            # Update state from tracker

            if not self.p.is_alive():
                self.logger.warning("Tracker stopped. Restarting...")
                self.p = Process(target=self.tracker.start, args=(self.queue,))
                self.p.start()

            if not self.queue.empty():
                self.state = self.queue.get()
                self.updated.set()

            gevent.sleep(0.01)
            self.updated.clear()
