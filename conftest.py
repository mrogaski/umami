# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass
