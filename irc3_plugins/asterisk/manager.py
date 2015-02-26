# -*- coding: utf-8 -*-
import panoramisk
try:
    from panoramisk import testing
except ImportError:
    pass


def get_manager(**kwargs):
    if 'testing' in kwargs:
        return testing.Manager(**kwargs)
    else:
        return panoramisk.Manager(**kwargs)
