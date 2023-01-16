
class Or:
    def __init__(self, *values) -> None:
        self.values = values


class And:
    def __init__(self, *values) -> None:
        self.values = values


class Not:
    def __init__(self, *values) -> None:
        self.values = values
