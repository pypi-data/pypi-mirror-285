from tkinter import Text

class Textarea(Text):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)

    def setValue(self, value: str) -> None:
        self.delete(1.0, "end")
        self.insert(1.0, value)

    def getValue(self) -> str:
        return self.get(1.0, "end-1c")
