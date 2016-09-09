from datetime import datetime


class Session:
    TIMESTAMP_FORMAT = '%Y%m%d%H%M%S'
    MAX_LENGTH_IN_MINUTES = 15

    def __init__(self):
        self.status = None
        self.id = None
        self.start_ts = None

    def __str__(self):
        return self.status + ' ' + self.id + ' ' + str(self.start_ts)

    def reset(self):
        self.status = None
        self.id = None
        self.start_ts = None

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(self.status + '\n')
            f.write(self.id + '\n')
            f.write(self.start_ts.strftime(Session.TIMESTAMP_FORMAT))

    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                self.status = f.readline()[:-1]
                self.id = f.readline()[:-1]
                self.start_ts = datetime.strptime(f.readline()[:-1], Session.TIMESTAMP_FORMAT)
        except FileNotFoundError:
            self.reset()
            return

    def is_active(self):
        if self.status != 'Approved':
            return False
        if len(self.id) < 1:
            return False
        now = datetime.utcnow()
        if now < self.start_ts:
            now = self.start_ts
            # raise Exception('System time seems to be out of sync:', datetime.utcnow(), self.start_ts)
        time_left = self.MAX_LENGTH_IN_MINUTES * 60 - (now - self.start_ts).seconds
        # API has no defined response for request with expired session id, so lets hope 2 second buffer is enough
        return time_left > 2