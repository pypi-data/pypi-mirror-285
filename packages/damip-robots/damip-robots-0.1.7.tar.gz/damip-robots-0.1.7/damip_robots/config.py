"""
Created on 06 28 23:54:20 2024

@project: damip
@author : kaiwei.li
@company: Digitopia Robotics Ltd.,Co.
"""

import os
import logging
import json

# Set logging level
logging.basicConfig(level=logging.INFO, format=':) %(asctime)s %(levelname)s: %(message)s')

redis_addr=[]

ID_FILE_PATH = '/usr/local/cfg/idmark.json'
DB_FILE_PATH = '/usr/local/cfg/maindb.json'

# Get idmark from file
def get_idmark(file_path):
    try:
        with open(file_path, 'r') as json_file:
            robot_data = json.load(json_file)#.encode(encoding='utf-8')
            robot_mark = robot_data['id']
            # print(robot_mark)
        return robot_mark
    except Exception as e:
        logging.error(":) load idmark json file failed!")

# Get maindb from file
def get_maindb(file_path):
    try:
        with open(file_path, 'r') as json_file:
            robot_data = json.load(json_file)#.encode(encoding='utf-8')
            redis_host = robot_data['redis_host']
            redis_port = robot_data['redis_port']
            redis_pswd = robot_data['redis_pswd']
            redis_addr = 'redis://:' + str(redis_pswd) + '@' + str(redis_host) + ':' + str(redis_port)
            # print(redis_addr)
        return redis_addr
    except Exception as e:
        logging.error(":) load maindb json file failed!")



# Redis list name
robot_idmark = get_idmark(ID_FILE_PATH)
robot_maindb = get_maindb(DB_FILE_PATH)

ROBOT_IDMARK = robot_idmark
REDIS_SERVER = robot_maindb

# logging.debug(":) load idmark json file success:" + ROBOT_IDMARK)
# logging.debug(":) load maindb json file success:" + REDIS_SERVER)

