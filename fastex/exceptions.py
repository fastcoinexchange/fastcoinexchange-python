class APIError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'FastCoinExchange APIError code: %s (%s)' % (self.code, self.msg)


class UnknownRequestMethod(Exception):
    def __init__(self, method):
        self.method = method

    def __str__(self):
        return 'Unknown request method: %s' % self.method