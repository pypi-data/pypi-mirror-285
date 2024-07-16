class DependencyNotFoundException(Exception):
    def __init__(self, interface, attrs) -> None:
        super().__init__(f"Dependency {interface} not found {attrs}")
