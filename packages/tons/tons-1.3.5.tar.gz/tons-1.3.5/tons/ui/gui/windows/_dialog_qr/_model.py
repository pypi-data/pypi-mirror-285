from typing import Optional

from PIL.Image import Image

from ...utils import qr_image, construct_transfer_uri


class DialogQRModel:
    def __init__(self,
                 address: str,
                 amount: Optional[int] = None,  # nanoton
                 text: Optional[str] = None):
        self._image = self._setup_image(address, amount, text)

    @staticmethod
    def _setup_image(address: str,
                     amount: Optional[int] = None,  # nanoton
                     text: Optional[str] = None):
        uri = construct_transfer_uri(address, amount, text)
        image = qr_image(uri)
        return image

    @property
    def image(self) -> Image:
        return self._image

