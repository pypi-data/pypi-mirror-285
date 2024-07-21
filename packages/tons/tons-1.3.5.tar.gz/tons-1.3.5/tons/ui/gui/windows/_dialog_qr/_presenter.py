from typing import Protocol

from PIL.Image import Image


class Model(Protocol):
    @property
    def image(self) -> Image: ...


class View(Protocol):
    def set_image(self, image: Image): ...


class DialogQRPresenter:
    def __init__(self, model: Model, view: View):
        super().__init__()
        self._model = model
        self._view = view
        self._display_model()

    def _display_model(self):
        image = self._model.image
        self._view.set_image(image)
