# -*- coding: utf-8 -*-

from .api import register_model

from fosforml.widgets.register_model import RegisterModel

from .decorators import scoring_func


__all__ = [
    'register_model'
]
