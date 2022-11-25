from fastapi.testclient import TestClient
import pytest
import sys
import csv
import os


#create a test-csv file and safe it in the same directory

def create_test_data():

    file_name = "colors.csv"
    file_path = "/ae/data/work/lb10732/"+file_name

    #if os.path.exists(file_name) == True:
        #print("File already exists")
        #skip the rest

    header = ["no", "color", "description"]
    data = [
        ["1", "red", "The color of blood"],
        ["2", "green", "The color of hope"],
        ["3", "blue", "The color of oceans"],
        ["4", "yellow", "The color of the sun"],
        ["5", "black", "The color of the night"],
        ]

    with open (file_path, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(header)

        writer.writerows(data)

#adding folder src/datarest to the system path
sys.path.insert(0, "/ae/data/work/lb10732/datarest/src/datarest")


if __name__=="__main__":
    create_test_data()
    print("Successful")