from dataclasses import dataclass


@dataclass
class Message:
    message: str


@dataclass
class Error:
    errors: str
