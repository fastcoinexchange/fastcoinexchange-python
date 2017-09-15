class FastexAPIError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'FastCoinExchange APIError "%s" (code: %s)' % (self.msg, self.code)


class FastexInvalidDataReceived(Exception):
    def __str__(self):
        return 'Invalid data received'


class FastexBadDataDecoded(Exception):
    def __str__(self):
        return 'Bad data decoded'
