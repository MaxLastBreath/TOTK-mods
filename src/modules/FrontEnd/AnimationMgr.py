import copy
import threading
from time import sleep
from modules.logger import log
from collections import deque


class AnimationQueue:
    isInit: bool = False
    queue = deque()

    __running: bool = True
    __lock = threading.Lock()

    @classmethod
    def Initialize(cls):

        log.warning("Initialize AnimationQueue")

        if cls.isInit:
            raise ("Already Initialized.")

        thread = threading.Thread(name="AnimationQueue", target=cls.UpdateQueue)
        thread.daemon = True
        thread.start()
        cls.isInit = True

    @classmethod
    def AddToQueue(cls, func):
        with cls.__lock:
            cls.queue.append(func)

    @classmethod
    def UpdateQueue(cls):
        while cls.__running:
            log.info("WEE")
            with cls.__lock:
                if len(cls.queue) > 0:
                    queue = cls.queue.copy()

                    for func in queue:
                        func()

            sleep(0.15)
