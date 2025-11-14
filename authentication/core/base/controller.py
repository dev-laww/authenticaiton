from abc import ABC

from .app import AppObject


class Controller(AppObject, ABC):
    """
    Abstract base class for controllers in the application.

    This class serves as a blueprint for all controller classes,
    ensuring they inherit common functionality and structure.
    """

    pass
