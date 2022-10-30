# -*- coding: utf-8 -*-
from itertools import count

import pytest


@pytest.fixture(scope="session")
def httpdbg_port_base():
    return count(4500)


@pytest.fixture()
def httpdbg_port(httpdbg_port_base):
    return next(httpdbg_port_base)