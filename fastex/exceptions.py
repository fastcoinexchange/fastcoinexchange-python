class FastexAPIError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'FastCoinExchange APIError "%s" (code: %s)' % (self.msg, self.code)
#
#
# class UnknownRequestMethod(Exception):
#     def __init__(self, method):
#         self.method = method
#
#     def __str__(self):
#         return 'Unknown request method: %s' % self.method
#
#
# class UnknownResponseKey(Exception):
#     def __init__(self, key):
#         self.key = key
#
#     def __str__(self):
#         return 'Unknown response key: %s' % self.key


class FastexInvalidDataReceived(Exception):
    def __str__(self):
        return 'Invalid data received'


class FastexBadDataDecoded(Exception):
    def __str__(self):
        return 'Bad data decoded'
