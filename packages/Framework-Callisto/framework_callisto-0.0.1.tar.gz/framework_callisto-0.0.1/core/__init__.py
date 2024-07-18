import json
import time
import random
import requests
import warnings

import callisto.core.config as mem

from ratelimit import limits, sleep_and_retry
from callisto.core.utils import dict_to_xml

warnings.filterwarnings('ignore') # Disable SSL related warnings