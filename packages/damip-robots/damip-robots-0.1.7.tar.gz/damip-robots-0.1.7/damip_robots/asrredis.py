"""
Created on 06 28 01:35:20 2024

@project: damip
@author : kaiwei.li
@company: Digitopia Robotics Ltd.,Co.
"""

import os
import aioredis
import asyncio
from datetime import datetime
import time

import logging

from damip_robots import config

from aioredis.exceptions import ConnectionError

# Set logging level
logging.basicConfig(level=logging.INFO, format=':) %(asctime)s %(levelname)s: %(message)s')

TIME_THRESHOLD = 5 # only handle asr result in threshold seconds

timestamp_record = None

format_str = '%Y-%m-%d %H:%M:%S'

def calculate_time_difference(timestamp1, timestamp2):
    try:
        # 将字符串转换为 datetime 对象
        time1 = datetime.strptime(timestamp1, format_str)
        time2 = datetime.strptime(timestamp2, format_str)

        # 计算时间间隔
        time_difference = time2 - time1

        # 将时间间隔转换为秒数
        seconds_difference = time_difference.total_seconds()

        # 输出时间间隔（以秒为单位）
        # print(f'Time difference in seconds: {seconds_difference}')
        return seconds_difference
    except ValueError as e:
        print(f"Error: {e}. Please provide timestamps in the format 'YYYY-MM-DD HH:MM:SS'.")


def check_asr_file():
    try:
        # 指定文件路径
        file_path = '/run/damip/damip_asr_client_audio_cache.wav'
        
        # 获取文件的最后修改时间
        modification_time = os.path.getmtime(file_path)
        
        # 使用time.strftime()格式化时间戳
        timestamp1 = str(time.strftime(format_str, time.localtime(modification_time)))

        # 获取当前时间
        timestamp2 = str(time.strftime(format_str, time.localtime()))

        # 计算文件修改时间
        time_diff = calculate_time_difference(timestamp1, timestamp2)

        if time_diff <= TIME_THRESHOLD:
            return True, time_diff
        else:
            return False, None
    except ValueError as e:
        print(f"Error: {e}. Check asr temp file failed. Please check it.")


async def sync_result():
    try:
        global timestamp_record

        # redis info
        redis = await aioredis.from_url(config.REDIS_SERVER)
        logging.info(f":) Redis server connection opened.")
        robot = str(config.ROBOT_IDMARK)
        # logging.info(":) Robot name:" + robot)
        
        # select db id
        redis_dbid = int(robot[-3:]) # get the last 3 number
        await redis.execute_command('SELECT', redis_dbid)
        # logging.info(':) Redis DB SELECT:' + str(redis_dbid))
        
        # get the last TRANS timestamp
        value = await redis.lindex('TRANS:'+robot[-8:], -1)
        value = value.decode('utf-8')
        timestamp1 = value[0:19]
        logging.info(":) Last TRANS Timpstamp1: " + timestamp1)

        if str(timestamp_record) == str(timestamp1):
            logging.info(":) Same timestamp, bypass")
            return False, 0, 0
        else:
            timestamp_record = timestamp1
        
        # get the nows LOCAL timestamp
        timestamp2 = str(time.strftime(format_str, time.localtime()))
        logging.info(":) Nows LOCAL Timpstamp2: " + timestamp2)
        time_diff = calculate_time_difference(timestamp1, timestamp2)
        logging.info(":) Timpstamp2-Timpstamp1: " + str(time_diff))

        if time_diff <= TIME_THRESHOLD:
            logging.info(":) Time_diff less than threshold, return True")
            # return False, 0, 0
            return True, time_diff, value[20:]
        else:
            logging.info(":) Time_diff too big, return False")
            return False, 0, 0

    except (ConnectionError, aioredis.exceptions.ConnectionError, aioredis.exceptions.TimeoutError) as e:
        logging.error(f":) Could not connect to Redis server: {e}")
        await asyncio.sleep(5)  # 等待一段时间后重试连接
    finally:
        if redis is not None:
            await redis.close()
            logging.info(f":) Redis server connection closed.")

