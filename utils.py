import csv
import json
import os
from pathlib import Path
from logging import Logger


from schema.csv_data import CsvData

# filename of where the csv data is stored in json
PINCODE_FILE_NAME = Path("temp/pincode_data.json")

def read_csv_data(file_name: str, logger: Logger):
    
    logger.info("[BACKGROUND_JOB] Trying to read %s ",file_name)
    
    try:
        
        data = {}
    
        with open(file_name, newline="") as file:
            reader = csv.reader(file)

            next(reader)  # skip header

            for row in reader:
                data[row[4]] = (
                    CsvData(
                        circlename=row[0],
                        regionname=row[1],
                        divisionname=row[2],
                        officename=row[3],
                        pincode=row[4],
                        officetype=row[5],
                        delivery=row[6],
                        district=row[7],
                        statename=row[8],
                        latitude=row[9],
                        longitude=row[10],
                    ).model_dump()
                )
        
        logger.info("[BACKGROUND_JOB] Completed reading and converting csv data")
        return data
    
    except Exception as e:
        raise Exception("error reading csv file",e)


def write_data_to_json(csv_data, logger: Logger) -> None:    
    
    logger.info("[BACKGROUND_JOB] Writing data to %s",PINCODE_FILE_NAME)
    try:
        
        if not os.path.exists(PINCODE_FILE_NAME):
            os.makedirs("temp")
        
        with open(PINCODE_FILE_NAME, "w") as json_file:
            json.dump(csv_data, json_file, indent=4)
    
        logger.info("[BACKGROUND_JOB] Data successfully wrote to %s",PINCODE_FILE_NAME)
    
    except Exception as e:
        raise Exception("Error writing csv data to json file", e)
        
        
def read_json_file(pincode:str) -> CsvData | None:
    
    try:
        with open(PINCODE_FILE_NAME) as f:
            
            data = json.load(f)
            
            if data[pincode]:
                return data[pincode]
            
    except Exception:
        return None

