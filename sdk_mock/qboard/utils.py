import datetime

class Logger:

    def __init__(self, verbosity = 0, log_logger = None):
        self.verbosity = verbosity
        self.log_logger = log_logger
    
    def log(self, msg, level):
        if level <= self.verbosity:
            now = datetime.datetime.now()
            timestamp = '[' + now.strftime("%Y-%m-%d %H:%M:%S") + '] '
            print(timestamp + msg)
            if self.log_logger != None:
                self.log_logger.info(msg)

def filter_params(params):
    res = {}
    for key in params:
        if params[key] != None:
            res[key] = params[key]
    return res

