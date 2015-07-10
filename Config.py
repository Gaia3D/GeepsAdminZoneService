# -*- coding: utf-8 -*-
import ConfigParser

class Config:
    log_mode = None
    log_file = None
    db_user = None
    db_pwd = None
    db_database = None

    def __init__(self, config_file):
        try:
            config = ConfigParser.RawConfigParser(allow_no_value=True)
            config.read(config_file)

            self.log_mode = config.get("log", "mode")
            self.log_file = config.get("log", "file")
            self.db_user = config.get("postgresql", "user")
            self.db_pwd = config.get("postgresql", "pwd")
            self.db_database = config.get("postgresql", "database")
        except Exception as e:
            print "[ERROR on read cfg] "+ str(e)