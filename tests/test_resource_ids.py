import pytest

from datarest._resource_ids import biz_key_composite_id, biz_hash_md5_id, biz_hash_sha256_id, uuid4_base64_id, create_id_default, IdEnum

def test_biz_key_composite_id():
    # Test with different primary key field values and separators
    assert biz_key_composite_id('foo', 'bar') == 'foo.bar'
    assert biz_key_composite_id('foo', 'bar', concat_sep='-') == 'foo-bar'
    assert biz_key_composite_id(1, 2) == '1.2'
    assert biz_key_composite_id(1, 2, concat_sep='-') == '1-2'
    
    # Test with empty fields
    assert biz_key_composite_id() == ''
    assert biz_key_composite_id('', '', concat_sep='-') == '-'
    
    # Test with non-string fields
    assert biz_key_composite_id(1, 2.5) == '1.2.5'
    assert biz_key_composite_id(1, 2.5, concat_sep='-') == '1-2.5'


def test_biz_hash_md5_id():
    # Test with different primary key field values and separators
    assert biz_hash_md5_id('foo', 'bar') == '04f98100995b2f5633210e10f21ee022'
    assert biz_hash_md5_id('foo', 'bar', concat_sep='-') == 'e5f9ec048d1dbe19c70f720e002f9cb1'
    assert biz_hash_md5_id(1, 2) == '56765472680401499c79732468ba4340'
    assert biz_hash_md5_id(1, 2, concat_sep='-') == '98c6f2c2287f4c73cea3d40ae7ec3ff2'

    # Test with empty fields
    assert biz_hash_md5_id() == 'd41d8cd98f00b204e9800998ecf8427e'
    assert biz_hash_md5_id('', '', concat_sep='-') == '336d5ebc5436534e61d16e63ddfca327'
    
    # Test with non-string fields
    assert biz_hash_md5_id(1, 2.5) == 'db3daece29a9d5f93d193ed25a4b973b'
    assert biz_hash_md5_id(1, 2.5, concat_sep='-') == '803be3e0b7294717669c8d98304b12e3'


def test_biz_hash_sha256_id():
    # Test with different primary key field values and separators
    assert biz_hash_sha256_id('foo', 'bar') == '2595d08ad22c733f7a1ce713e767563e13a8dfa35baa74919c28e0f586cb424b'
    assert biz_hash_sha256_id('foo', 'bar', concat_sep='-') == '7d89c4f517e3bd4b5e8e76687937005b602ea00c5cba3e25ef1fc6575a55103e'
    assert biz_hash_sha256_id(1, 2) == '77ac319bfe1979e2d799d9e6987e65feb54f61511c03552ebae990826c208590'
    assert biz_hash_sha256_id(1, 2, concat_sep='-') == '412a4789b02cad19bacb029f5c8ec8e9b115375d82b97df1d6b15997a8e70e01'

    # Test with empty fields
    assert biz_hash_sha256_id() == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    assert biz_hash_sha256_id('', '', concat_sep='-') == '3973e022e93220f9212c18d0d0c543ae7c309e46640da93a4a0314de999f5112'
    
    # Test with non-string fields
    assert biz_hash_sha256_id(1, 2.5) == '0a5d71a53024d9d6a410062789da3fe155ba44cca15210791fb8ae09c749426c'
    assert biz_hash_sha256_id(1, 2.5, concat_sep='-') == '3b3f05951ac4b7cf9aa36a980887301e9c14ea47dc5de8117147d74187029869'


def test_uuid4_base64_id():
    # two random UUIDs should be different
    id1 = uuid4_base64_id()
    id2 = uuid4_base64_id()
    assert id1 != id2  

    #Can there be more test cases?
    

# möglichkeit des parametisierens fürs mapping?

def test_create_id_default():

    # Test with different ID types
    id_type = IdEnum.biz_key
    default_func = create_id_default(id_type)
    assert default_func is None
    
    """
    id_type = IdEnum.biz_key_composite
    default_func = create_id_default(id_type, primary_key=('field1', 'field2'))
    assert default_func({'current parameters':{'field1': 'foo', 'field2': 'bar'}}) == 'foo.bar'
    
    id_type = IdEnum.biz_hash_md5
    default_func = create_id_default(id_type, primary_key=('field1', 'field2'))
    assert default_func({'field1': 'foo', 'field2': 'bar'}) == '2f7a9f1bce82e94d5e5f5c5ca3f5d5b5'
    
    id_type = IdEnum.biz_hash_sha256
    default_func = create_id_default(id_type, primary_key=('field1', 'field2'))
    assert default_func({'field1': 'foo', 'field2': 'bar'}) == '4735c09b5d5f2d3a3a8e03b7cc17e16c2f3b3edde16e776f7a70a0e843f3b3e3'
    """
    # Test-Output: FAILED test_resource_ids.py::test_create_id_default - AttributeError: 'dict' object has no attribute 'current_parameters'
    # .current_parameters kann nicht auf das übergebene dictionary angewendet werden
    # Erst wird die extra id column erzeugt und hinzugefügt (wohin wird es hinzugefügt? Was wird an SQLModel letzten Endes übergeben?)
    # Was genau wird an "create_id_default" übergeben?


    # Test with an unsupported ID type
    id_type = 'invalid'
    with pytest.raises(KeyError):
        create_id_default(id_type)