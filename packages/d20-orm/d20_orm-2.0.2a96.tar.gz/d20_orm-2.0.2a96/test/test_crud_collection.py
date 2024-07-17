from test_basic_element_test import BasicElementTest
import test_params as test_params

db_name='UNIT_TEST'
conf={'DBURL':test_params.local_adb_url, 'DBUSERNAME':test_params.local_adb_username, 'DBPASSWORD':test_params.local_adb_password}

basic_elemet = BasicElementTest('create', {'test': 'success'},conf=conf, db_name=db_name)

