import json
import dateparser
import numpy as np
import math
import logging
import datetime
import pytz

logger = logging.getLogger(__name__)

class log_collection:
  
  # stations holds all stations data objects
  stations = {}

  def __init__(self):
    pass
