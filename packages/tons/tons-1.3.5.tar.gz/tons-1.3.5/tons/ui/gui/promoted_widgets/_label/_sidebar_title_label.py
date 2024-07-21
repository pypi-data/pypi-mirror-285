from PyQt6.QtWidgets import QLabel


class SideBarTitleLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = self.font()
        font.setPointSize( round(font.pointSize() * 11 / 13) )
        font.setWeight(700)
        self.setFont(font)
