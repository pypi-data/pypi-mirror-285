from typing import Dict, Optional, Union


class VariableType(str):
    TEXT = "text"
    JSON = "json"
    

class Variable():
    def __init__(self, type: str, payload: Dict[str, Union[str, int, bool]]):
        self.type = type
        self.payload = payload

    def to_json(self):
        return {
            "type": self.type,
            "payload": self.payload
        }

class DatasetEntry():
    def __init__(self, input: Variable, context: Optional[Variable] = None, expectedOutput: Optional[Variable] = None):
        self.input = input
        self.context = context
        self.expectedOutput = expectedOutput

    def to_json(self):
        return_dict = {}
        if self.input is not None:
            return_dict["input"] = {
                "type": self.input['type'],  # type: ignore
                "payload": self.input['payload']  # type: ignore
            }
        if self.context is not None:
            return_dict["context"] = {
                "type": self.context['type'], # type: ignore
                "payload": self.context['payload'] # type: ignore
            }
        if self.expectedOutput is not None:
            return_dict["expectedOutput"] = {
                "type": self.expectedOutput['type'], # type: ignore
                "payload": self.expectedOutput['payload'] # type: ignore
            }
        return return_dict
        