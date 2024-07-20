class MessageHandler:
    def __init__(self):
        self.message_types = {}

    def add_message_type(self, message_type: str, handler):
        self.message_types[message_type] = handler

    def handle_message(self, message_type: str, data: dict):
        if message_type in self.message_types:
            return self.message_types[message_type](data)
        return "Message type not supported."