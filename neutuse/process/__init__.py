from .engine import Engine
# from .spec.skeletonize import skeletonize

import glob
import os

_cd = os.path.split(__file__)[0]
for full_name in glob.glob(os.path.join(_cd,'spec/*.py')):
    file_name = os.path.split(full_name)[1]
    if not file_name.startswith('_'):
        exec(open(full_name).read())
