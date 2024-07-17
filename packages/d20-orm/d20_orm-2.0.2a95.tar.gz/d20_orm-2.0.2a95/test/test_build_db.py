from GraphClassFactory import ClassFactory
import test_params as test_params

def test_build_db():
    graphname = 'test_graph'
    collections = ['orphan1', 'orphan2']
    edgeDefinitions={'edge1': {'fromCollections': ['collection1','collection2'],'toCollections': ['collection4','collection3']}}
    db_name='UNIT_TEST'
    conf={'DBURL':test_params.local_adb_url, 'DBUSERNAME':test_params.local_adb_username, 'DBPASSWORD':test_params.local_adb_password}
    factory = ClassFactory(graphname, db_name, collections = collections, edgeDefinitions=edgeDefinitions, conf=conf)
    print(factory)


test_build_db()