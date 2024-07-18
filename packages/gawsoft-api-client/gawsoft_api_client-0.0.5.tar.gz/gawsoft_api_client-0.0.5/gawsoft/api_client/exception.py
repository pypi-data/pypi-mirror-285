class ApiException(Exception):
    def __init__(self, status=None, reason=None, http_resp=None):

        if http_resp:
            self.status = http_resp.status_code
            self.reason = http_resp.reason
            self.response = http_resp
        else:
            self.status = status
            self.reason = reason
            self.response = None

    def __str__(self):
        """Custom error messages for exception"""
        error_message = "({0})\n"\
                        "Reason: {1}\n".format(self.status, self.reason)
        if 'headers' in self and self.headers:
            error_message += "HTTP response headers: {0}\n".format(
                self.headers)

        if 'body' in self and self.body:
            error_message += "HTTP response body: {0}\n".format(self.body)

        return error_message