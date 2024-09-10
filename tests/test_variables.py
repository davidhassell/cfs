from core.db.standalone import setup_django
from pathlib import Path
from cfdm import cellmethod

import pytest

###
### This test file concentrates on the issues around variable import and querying
###
CELL_TEST_DATA = [
     ('latitude','mean'),
     ('longitude','mean'),
     ('time', 'mean')
]

STD_DOMAIN_PROPERTIES = {'name':'N216','region':'global','nominal_resolution':'10km',
                            'size':1000,'coordinates':'longitude,latitude,pressure'}

@pytest.fixture(scope="session", autouse=True)
def setup_test_db(tmp_path_factory):
    """ 
    Get ourselves a db to work with. Note that this database is progressively
    modified by all the tests that follow. So if you're debugging tests, you 
    have to work though them consecutively. 
    """
    tmp_path = tmp_path_factory.mktemp('testing_interface')
    dbfile = str(Path(tmp_path)/'test.db')
    migrations_location = str(Path(tmp_path)/'migrations')
    setup_django(db_file=dbfile,  migrations_location=migrations_location)

@pytest.fixture
def test_db():
    """ 
    This database (and it's contents) is used in all the following
    tests, and is progressively modified as the tests proceed.
    """
    from core.db.interface import CollectionDB
    return CollectionDB()


def test_simple_variable(test_db):
    properties = {'identity':'test var 1','atomic_origin':'imaginary','temporal_resolution':'daily',
                  'domain':STD_DOMAIN_PROPERTIES}
    var = test_db.variable_retrieve_or_make(properties)

def test_sharing_domain(test_db):
    properties = {'identity':'test var 2','atomic_origin':'imaginary','temporal_resolution':'monthly',
                  'domain':STD_DOMAIN_PROPERTIES}
    var = test_db.variable_retrieve_or_make(properties)
    assert len(test_db.domains_all()) == 1
    assert len(test_db.variables_all()) == 2

def test_not_sharing_domain(test_db):
    domain_properties = {'name':'N216','region':'global','nominal_resolution':'10km',
                            'size':1000,'coordinates':'longitude,latitude,levels'}
    properties = {'identity':'test var 3','atomic_origin':'imaginary','temporal_resolution':'monthly',
                  'domain':domain_properties}
    var = test_db.variable_retrieve_or_make(properties)
    assert len(test_db.domains_all()) == 2
    assert len(test_db.variables_all()) == 3

def test_creating_variable_with_properties(test_db):
    properties = {'identity':'test var 4','atomic_origin':'imaginary','temporal_resolution':'daily',
                  'domain': STD_DOMAIN_PROPERTIES,
                  'experiment':'mytest','institution':'Narnia'}
    var = test_db.variable_retrieve_or_make(properties)
    print(test_db.variables_all())
    assert len(test_db.variables_all()) == 4

def test_retrieving_by_property_keys(test_db):
    variables = test_db.variables_retrieve_by_key('experiment','mytest')
    print(variables)

def test_cell_methods_create(test_db):
    """ 
    Test creating a variable with cell methods in the properties 
    """
    properties = {'identity':'test var 5','atomic_origin':'imaginary','temporal_resolution':'monthly',
                  'domain':STD_DOMAIN_PROPERTIES,
                  'cell_methods':CELL_TEST_DATA}
    var = test_db.variable_retrieve_or_make(properties)

def test_querying_cell_methods(test_db):
    """
    Find all variables with a time: mean cell method and monthly data
    """
    # first create another one to create trouble 
    props = {'temporal_resolution':'monthly', 'cell_methods':[('time','mean'),]}
    var1 = test_db.variables_retrieve_by_properties(props)
    var2 = test_db.variables_retrieve_by_properties({'identity':'test var 5'})
    assert len(var1) == 1
    assert var1[0] == var2[0]

def test_file_variable_collection(test_db):
    file_properties ={'name':'test_file_1','path':'/nowhere/','size':10}
    v = test_db.variables_retrieve_by_properties({'identity':'test var 5'})[0]
    f = test_db.file_retrieve_or_make(file_properties)
    c = test_db.collection_create('Holding')
    test_db.variable_add_to_file_and_collection(v, f, c.name)
    var2 = test_db.variables_retrieve_by_properties({'in_file':f})    
    assert var2[0] == v
    var2 =  test_db.variables_retrieve_by_properties({'in_file':file_properties})    
    assert var2[0] == v
    var2 = test_db.variables_retrieve_by_properties({},from_collection=c)
    assert var2[0] == v
    var2 = test_db.variables_retrieve_by_properties({'identity':'fred'}, from_collection=c)
    assert len(var2) == 0
    var2 = test_db.variables_retrieve_by_properties({'identity':'test var 5'}, from_collection=c)
    assert var2[0] == v




    

    
    








