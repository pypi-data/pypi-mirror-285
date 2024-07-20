# app/operational_layer/operational_layer.py
import logging
from .message_handler import MessageHandler
from .tool_manager import ToolManager


class OperationalLayer:
    def __init__(self):
        self.message_handler = MessageHandler()
        self.tool_manager = ToolManager()

    def manage_input_output(self, query: str) -> str:
        pass

    def manage_logging(self, log: str):
        logging.info(log)

    def manage_temporary_storage(self, temp_data: str) -> str:
        pass