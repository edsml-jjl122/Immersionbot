class Log_constructor():
    def __init__(self, duid, media_type, amount, title, note, created) -> None:
        self.duid = duid
        self.media_type = media_type
        self.amount = amount
        self.title = title
        self.note = note
        self.created_at = created

    def print(self):
        print(f'{self.duid} │ {self.media_type} │ {self.amount} │ {self.title} │ {self.note} │ {self.created_at}')