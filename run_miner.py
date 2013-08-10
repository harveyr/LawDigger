from lawdiffs.mine import miner
from lawdiffs.data import models
from lawdiffs.data.access import Session
from lawdiffs.data.access import laws as da_laws

session = Session()

session.query(models.Law).delete()
session.query(models.LawDivision).delete()
session.query(models.LawCode).delete()
session.commit()

# session = data.Session()
# law = models.Law('1.010')

# session.add(law)
# session.commit()

p = miner.OrLawParser()
p.run()
