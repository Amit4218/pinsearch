from datetime import datetime


import requests
from utils import read_csv_data, write_data_to_json
from cron.datafile_scraper import DataFileScraper
from logger import logger



def pincode_update_job():
    try:
        logger.info("[BACKGROUND_JOB] Pincode update task started at %s",datetime.now())

        csv_file = DataFileScraper(logger=logger).start()
        
        if csv_file:
        
            csv_data = read_csv_data(file_name=csv_file, logger=logger)
        
            write_data_to_json(csv_data=csv_data, logger=logger)

        logger.info("[BACKGROUND_JOB] job completed successfully at %s", datetime.now())

    except requests.RequestException as e:
        logger.exception("[BACKGROUND_JOB] Download failed: %s", e)

    except OSError as e:
        logger.exception("[BACKGROUND_JOB] File operation failed: %s", e)

    except Exception as e:
        logger.exception("[BACKGROUND_JOB] Unexpected error: %s", e)