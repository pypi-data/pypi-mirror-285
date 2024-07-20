class RequestHandler:
    def __init__(self):
        self.request_types = {}

    def add_request_type(self, request_type: str, handler):
        self.request_types[request_type] = handler

    def handle_request(self, request_type: str, data: dict):
        if request_type in self.request_types:
            return self.request_types[request_type](data)
        return "Request type not supported."