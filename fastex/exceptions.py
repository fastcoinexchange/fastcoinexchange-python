class FastexAPIError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'FastCoinExchange APIError "%s" (code: %s)' % (self.msg, self.code)


class FastexInvalidDataReceived(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return 'Invalid data received. Have got "%s"' % (self.data,)


class FastexBadDataDecoded(Exception):
    def __str__(self):
        return 'Bad data decoded'


class AccountDisabled(Exception):
    def __str__(self):
        return 'Account is disabled'


class FastexPrivateRequestsDisabled(Exception):
    def __str__(self):
        return 'It`s impossible to make a private request without a fastex id, a public key, a private key or a ' \
               'server key definition.'
