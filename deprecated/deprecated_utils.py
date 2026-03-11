import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

with open('C:/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/export/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
