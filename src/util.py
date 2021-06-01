#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Bruce_H_Cottman"
__license__ = "MIT License"
__coverage__ = 0.98



from typing import Dict, List
from loguru import logger

import numpy as np
import pandas as pd
from pandas.core.dtypes.generic import ABCDataFrame
from numba import jit

#
import warnings

warnings.filterwarnings("ignore")


class janitor_Error(Exception):
    pass


def raise_janitor_Error(msg):
    logger.error(msg)
    raise janitor_Error(msg)


####  for interna use


