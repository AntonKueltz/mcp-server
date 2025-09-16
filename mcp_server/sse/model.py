class ServerSentEvent:
    event: str | None
    data: str | None
    id: str | None
    retry: int | None

    def __init__(
        self,
        event: str | None = None,
        data: str | None = None,
        id: str | None = None,
        retry: int | None = None,
    ):
        self.event = event
        self.data = data
        self.id = id
        self.retry = retry

    def serialize(self) -> str:
        data_str = None
        if self.data:
            data_str = "\n".join((f"data: {line}" for line in self.data.split("\n")))

        formatted = (
            (f"event: {self.event}\n" if self.event else "")
            + (f"{data_str}\n" if data_str else "")
            + (f"id: {self.id}\n" if self.id else "")
            + (f"retry: {self.retry}\n" if self.retry else "")
        )

        if not formatted:
            raise ValueError("ServerSentEvent has no data")

        return formatted + "\n"
