#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This script is just housing the dependencies for the other scripts in the src folder.
It is not intended to be run as a script.
The dependencies are:
    - pathlib
    - pandas
possible future dependencies:
    - csv
'''

import pandas as pd
import pathlib as pl
from functools import reduce
from typing import Union, Tuple, Optional, List, Dict
import datetime as dt
import re
