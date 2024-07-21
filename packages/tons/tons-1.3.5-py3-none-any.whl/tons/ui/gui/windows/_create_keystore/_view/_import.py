import os.path

from PyQt6.QtCore import Qt

from ._create import CreateKeystoreView


class ImportKeystoreView(CreateKeystoreView):  # TODO refactor SOLID
    def __init__(self, path_to_file: str):
        super().__init__()
        file_name = os.path.basename(path_to_file)
        self.setWindowTitle(f'New keystore (imported from {file_name})')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
