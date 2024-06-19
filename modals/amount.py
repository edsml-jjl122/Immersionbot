class Amount():
    def __init__(self, bool, amount) -> None:
        self.bool = bool
        self.value = amount

    def print(self):
        print(f'{self.duid} │ {self.media_type} │ {self.amount} │ {self.title} │ {self.note} │ {self.created_at}')