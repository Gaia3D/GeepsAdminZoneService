# -*- coding: utf-8 -*-
import ConfigParser

class Config:
    log_mode = None
    log_file = None
    db_user = None
    db_pwd = None
    db_database = None
    crs_list = None
    download_folder = None
    image_folder = None

    def __init__(self, config_file):
        try:
            config = ConfigParser.RawConfigParser(allow_no_value=True)
            config.read(config_file)

            self.log_mode = config.get("log", "mode")
            self.log_file = config.get("log", "file")

            self.db_user = config.get("postgresql", "user")
            self.db_pwd = config.get("postgresql", "pwd")
            self.db_database = config.get("postgresql", "database")

            self.crs_list = eval("["+config.get("crs", "crs_list")+"]")

            self.download_folder = config.get("download", "folder")

            self.image_folder = config.get("image", "folder")

        except Exception as e:
            print "[ERROR on read cfg] " + str(e)
            exit()