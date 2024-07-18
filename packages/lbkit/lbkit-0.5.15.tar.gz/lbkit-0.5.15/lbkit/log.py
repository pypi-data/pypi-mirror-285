import logging
import os
from lbkit.misc import Color

class Logger(logging.getLoggerClass()):

    def __init__(self, *args, **kwargs):
        super(Logger, self).__init__(*args, **kwargs)
        self.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        log = os.environ.get("LOG")
        if log is None:
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)s] %(message)s')
            if log == "info":
                self.setLevel(logging.INFO)
            elif log == "warn":
                self.setLevel(logging.WARNING)
            elif log == "error":
                self.setLevel(logging.ERROR)
            else:
                self.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self.handlers = []
        self.addHandler(handler)

    def error(self, msg, *args, **kwargs):
        msg = Color.RED + msg + Color.RESET_ALL
        super(Logger, self).error(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        msg = Color.YELLOW + msg + Color.RESET_ALL
        super(Logger, self).warning(msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        msg = Color.GREEN + msg + Color.RESET_ALL
        super(Logger, self).info(msg, *args, **kwargs)

