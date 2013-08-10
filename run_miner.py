from lawdiffs.mine import miner
from lawdiffs.data import models
from lawdiffs.data.client import mongoengine_connect
from lawdiffs.data.access import laws as data_laws

mongoengine_connect()

p = miner.OrLawParser()
p.run()
