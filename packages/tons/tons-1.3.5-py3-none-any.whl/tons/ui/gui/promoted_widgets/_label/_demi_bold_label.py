from PyQt6.QtWidgets import QLabel


class Weight700Label(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = self.font()
        font.setWeight(700)
        self.setFont(font)
