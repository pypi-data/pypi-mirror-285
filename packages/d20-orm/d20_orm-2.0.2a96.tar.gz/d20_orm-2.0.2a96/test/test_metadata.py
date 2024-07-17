import os
import json

os.environ['DBPREFIX'] = 'MD_UNIT_TEST_'
os.environ['DBUSERNAME'] = "root"
os.environ['DBPASSWORD'] = "M45v&Mgc7"
os.environ['DBURL'] = json.dumps(['http://127.0.0.1:8529/'])


from Metadata import Metadata

md_test = Metadata()

