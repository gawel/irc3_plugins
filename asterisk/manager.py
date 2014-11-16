# -*- coding: utf-8 -*-
import panoramisk
from panoramisk import testing


def get_manager(**kwargs):
    if 'testing' in kwargs:
        return testing.Manager(**kwargs)
    else:
        return panoramisk.Manager(**kwargs)
