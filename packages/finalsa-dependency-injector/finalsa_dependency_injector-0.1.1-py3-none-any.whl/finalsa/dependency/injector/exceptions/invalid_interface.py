class InvalidInterface(Exception):
    def __init__(self, interface, cls) -> None:
        super().__init__(f"Invalid implementation {cls} for {interface}")
