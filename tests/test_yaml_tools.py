import pytest
import yaml
import sys
import decimal
from io import StringIO

from datarest._yaml_tools import str_representer, dump_as_str, dump_decimal_as_str


def test_str_representer():
    # Create a Dumper object for use in the tests
    dumper = yaml.Dumper(stream=sys.stdout) #über StringIO-Objekte versuchen

    int_string = 123
    str_string = "abc"
    list_string = [1, 2, 3]

    # Test with different types of data
    assert str_representer(dumper, int_string).value == "123"
    assert str_representer(dumper, str_string).value == "abc"
    assert str_representer(dumper, list_string).value == "[1, 2, 3]"

    # Test with an object of the decimal.Decimal class
    # does implicitly test the function dump_decimal_as_str()
    decimal_obj = decimal.Decimal("1.2345")
    assert str_representer(dumper, decimal_obj).value == "1.2345"



def test_dump_as_str():
    
    # Define a sample class to use in the tests
    @dump_as_str
    class TestClass:
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return str(self.value)

    test_obj = TestClass(123)
    yaml_str = yaml.dump(test_obj)

    assert yaml_str == "'123'\n"
    #test fails -> yaml_str returns pointer to yaml_str

    """
    # Define a sample class to use in the tests
    @dump_as_str
    class TestClass:
        pass

    class Testclass_2:
        pass

    test_obj = TestClass()
    test_obj_2 = Testclass_2()
    """

    """
    with open("document.yaml", "w") as stream:
        yaml.dump(test_obj, stream)
    with open("document_2.yaml", "w") as stream_2:
        yaml.dump(test_obj_2, stream_2)
    """
    #breakpoint()
    #assert isinstance(yaml_str, str)
    #assert isinstance(yaml_str_2, str)
    #cannot see a difference between these two classes -> always get the pointer as a return (__repr__() == __str__())


def test_dump_as_str_inheritance():
    
    @dump_as_str
    class BaseClass:
        def __str__(self):
            return "base class string representation"

    # Create a subclass of the base class
    @dump_as_str
    class SubClass(BaseClass):
        pass

    # Dump an instance of the subclass to a YAML string
    yaml_str = yaml.dump(SubClass())

    # Check that the resulting YAML string contains the expected string representation of the object
    assert "base class string representation" in yaml_str


if __name__=="__main__":
    test_dump_as_str()


