#contains trials and other stuff which helps understanding the code

import pytest
import csv
import os
from pydantic import BaseModel, Field
from pathlib import Path
import typer
import yaml
import sys

from datarest._yaml_tools import str_representer, dump_as_str

#create a test-csv file and safe it in the same directory
def create_test_data_csv():

    file_name = "countries.csv"
    file_path = "/ae/data/work/lb10732/datarest/tests/"+file_name

    FileExists = os.path.exists(file_path)  

    if FileExists == True:
        print("Data already exists")
    else:
        header = ["no", "name", "capital"]
        data = [
            ["1", "germany", "berlin"],
            ["2", "france", "paris"],
            ["3", "austria", "vienna"],
            ["4", "czech_republic", "prague"],
            ["5", "poland", "warsaw"]]

        with open (file_path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)

def save_test_data_as_str():
    #with open (filepath="countries.csv", "r") as file:
        example_data = str(file.readlines())
        return example_data
        

@pytest.mark.skip
def test_app_config():
    test_table_path = Path("countries.csv")
    test_table = test_table_path.stem.lower()
    test_config = app_config(table=test_table, title="TEST")
    return test_config
    assert isinstance(test_config, AppConfig) == True
    assert test_config.datarest.fastapi.app.title == "TEST API"
 

def check_for_type():
    #helper function
    with open ("colors.csv", "r") as file:
        file_type = type(file)
        print(file_type)



    """
    # Create a Dumper object for use in the tests
    dumper = yaml.Dumper(stream=sys.stdout)
    
    # Check that the custom representer has been registered for the SampleClass
    assert dumper.yaml_representers[SampleClass] == str_representer
    assert dumper.yaml_representers[SampleClass] == str_representer

    # Create an object of the SampleClass and check that it is dumped as a string
    sample_obj = SampleClass()
    assert dumper.represent_data(sample_obj) == dumper.represent_str(str(sample_obj))
    """


def test_dump_decimal_as_str():
    # Dump a Decimal object as a string
    dump_decimal_as_str()
    data = {'price': decimal.Decimal('12.34')}
    expected_output = 'price: "12.34"\n'
    output = yaml.dump(data)
    assert output == expected_output

if __name__=="__main__":
    #create_test_data_csv()
    #test_app_config(example_data)
    #test_config = test_app_config()
    #print(type(test_config))
    #test_path = Path("countries_app.yaml")
    #write_app_config(test_path, test_config)
    
    class ExampleClass:
        def __init__(self, value):
            self.value = value
    
    example_obj = ExampleClass(123)
    data = yaml.dump(example_obj)
    print(data)
    print(type(data))
    

    @dump_as_str
    class TestClass:
        def __init__(self, value):
            self.value = value
    
    test_obj = TestClass(123)
    data_1 = yaml.dump(test_obj)
    print(data_1)
    print(type(data_1))
    
    print("Successful")