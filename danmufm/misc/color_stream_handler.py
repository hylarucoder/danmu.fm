import logging
import curses


class ColorStreamHandler(logging.Handler):
    def __init__(self, use_colors):
        logging.Handler.__init__(self)
        self.use_colors = use_colors

        # Initialize environment
        curses.setupterm()

        # Get the foreground color attribute for this environment
        self.fcap = curses.tigetstr('setaf')

        # Get the normal attribute
        self.COLOR_NORMAL = curses.tigetstr('sgr0').decode("utf-8")

        # Get + Save the color sequences
        self.COLOR_INFO = curses.tparm(self.fcap, curses.COLOR_GREEN).decode("utf-8")
        self.COLOR_ERROR = curses.tparm(self.fcap, curses.COLOR_RED).decode("utf-8")
        self.COLOR_WARNING = curses.tparm(self.fcap, curses.COLOR_YELLOW).decode("utf-8")
        self.COLOR_DEBUG = curses.tparm(self.fcap, curses.COLOR_BLUE).decode("utf-8")

    def color(self, msg, level):
        if level == "INFO":
            return "%s%s%s" % (self.COLOR_INFO, msg, self.COLOR_NORMAL)
        elif level == "WARNING":
            return "%s%s%s" % (self.COLOR_WARNING, msg, self.COLOR_NORMAL)
        elif level == "ERROR":
            return "%s%s%s" % (self.COLOR_ERROR, msg, self.COLOR_NORMAL)
        elif level == "DEBUG":
            return "%s%s%s" % (self.COLOR_DEBUG, msg, self.COLOR_NORMAL)
        else:
            return msg

    def emit(self, record):
        # record.msg = record.msg.encode('utf-8', 'ignore')
        msg = self.format(record)

        # This just removes the date and milliseconds from asctime
        temp = msg.split(']')
        msg = '[' + temp[0].split(' ')[1].split(',')[0] + ']' + temp[1]
        if self.use_colors:
            msg = self.color(msg, record.levelname)
        print(msg)
