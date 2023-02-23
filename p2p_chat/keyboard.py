import threading

class KeyboardThread(threading.Thread):
    def __init__(self, callback = None, name = "keyboard-thread"):
        self.callback = callback
        super(KeyboardThread, self).__init__(name = name)
        self.start()

    def run(self):
        print(True)
        while True:
            print(False)
            # try:
            self.callback(input())
            # except KeyboardInterrupt:
            #     raise
            #     break
            # except:
            #     break