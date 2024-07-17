from . import gw
from xaal.lib import aiohelpers

aiohelpers.run_async_package(gw.PACKAGE_NAME,gw.setup)
