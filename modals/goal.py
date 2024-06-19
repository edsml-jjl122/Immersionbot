class Goal():
    def __init__(self, duid, type, media_type, current_amount, amount, text, span, created_at, end) -> None:
        self.duid = duid
        self.goal_type = type
        self.media_type = media_type
        self.current_amount = current_amount
        self.amount = amount
        self.text = text
        self.span = span
        self.created_at = created_at
        self.end = end

    def where_clause(self):
        return f"WHERE discord_user_id = {self.duid} and goal_type = '{self.goal_type}' and media_type = '{self.media_type.value}' and amount = {self.amount} and text = '{self.text}' and span = '{self.span}' and created_at = '{self.created_at}' and end = '{self.end}'"