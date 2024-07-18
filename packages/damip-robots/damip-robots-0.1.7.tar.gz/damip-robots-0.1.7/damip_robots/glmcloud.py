"""
Created on 06 09 21:35:20 2024

@project: damip
@author : kaiwei.li
@company: Digitopia Robotics Ltd.,Co.
"""

import re
import aioredis
import asyncio
from datetime import datetime
import json

import logging

from zhipuai import ZhipuAI

from damip_robots import config

from aioredis.exceptions import ConnectionError

# Set logging level
logging.basicConfig(level=logging.INFO, format=':) %(asctime)s %(levelname)s: %(message)s')

format_str = '%Y-%m-%d %H:%M:%S'

# get glm apikey and prompt from redis
async def init():
    try:
        redis = aioredis.from_url(config.REDIS_SERVER)
        logging.info(f":) Redis server connection opened.")
        
        # load apikey
        value = await redis.get('PARAM:ZHIPU:APIKEY')
        REDIS_ZHIPU_APIKEY = value
        
        # load prompt
        value = await redis.get('PARAM:ZHIPU:PROMPT')
        try:
            json_data = json.loads(value)#.encode(encoding='utf-8')
            REDIS_ZHIPU_PROMPT = json_data['prompt']
            REDIS_ZHIPU_PREFIX = json_data['prefix']
            REDIS_ZHIPU_SUFFIX = json_data['suffix']
            # print(":) REDIS_ZHIPU_PROMPT is ", REDIS_ZHIPU_PROMPT)
            # print(":) REDIS_ZHIPU_PREFIX is ", REDIS_ZHIPU_PREFIX)
            # print(":) REDIS_ZHIPU_SUFFIX is ", REDIS_ZHIPU_SUFFIX)
        except json.JSONDecodeError as e:
            logging.info(':) Could not decode JSON: ' + {e})
        
        return REDIS_ZHIPU_APIKEY, REDIS_ZHIPU_PROMPT, REDIS_ZHIPU_PREFIX, REDIS_ZHIPU_SUFFIX

    except ConnectionError as e:
        REDIS_ZHIPU_APIKEY = ""
        REDIS_ZHIPU_PROMPT = ""
        logging.info(':) Could not connect to Redis: ' + {e})
    finally:
        await redis.close()
        logging.info(f":) Redis server connection closed.")


# find functions in answer
def extract(answer):
    functions_args = []
    functions_name = []
    """
    提取字符串中所有DIGITOPIA.后面的函数名和括号内的参数。

    参数:
    s (str): 包含函数调用的字符串。

    返回:
    list: 包含所有匹配项的列表，每个匹配项是一个元组(函数名, 参数)。
    """
    # 使用正则表达式匹配所有函数调用
    matches = re.findall(r'DIGITOPIA\.(.*?)\((.*?)\)', answer)

    for function_name, function_args in matches:
        # logging.info("函数:" + function_name)
        # logging.info("参数:" + function_args)
        functions_name.append(function_name)
        functions_args.append(function_args)
    
    return functions_name, functions_args


# transfer functions to index
def transfer(functions_name, functions_args):
    functions_index = []
    for function_name, function_args in zip(functions_name, functions_args):
        # logging.info("function_name:" + function_name)
        # logging.info("function_args:" + function_args)

        if "head_shake" in function_name:
            functions_index.append(1)
        elif "left_arm_shake" in function_name:
            functions_index.append(2)
        elif "right_arm_shake" in function_name:
            functions_index.append(3)
        elif "wheels_move" in function_name:
            functions_index.append(4)
        elif "voice_play" in function_name:
            functions_index.append(9)
        else:
            functions_index.append(0)
    return functions_index


# glm cloud
def request(usr_ask):

    # add prefix and suffix
    question = prefix + usr_ask + suffix
    logging.info(":) GLM cloud request: " + question)

    # glm message
    messages=[
    {"role": "user", "content": prompt},
    {"role": "user", "content": question}
    ]

    # glm client
    response = client.chat.completions.create(
    model="glm-4",  # 填写需要调用的模型名称
    messages=messages,
    top_p=0.7,
    temperature=0.7,
    max_tokens=1024,
    stream=True,
    )
   
    answer_count = 0
    answer_total = ""

    for trunk in response:
        
        answer_count = answer_count + 1
        # timestamp = str(time.strftime(format_str, time.localtime()))
        
        answer_block = trunk.choices[0].delta.content
        # print(":) answer_block = ", answer_block, ", answer_count = ", answer_count)
        
        answer_total = str(answer_total) + str(answer_block)
        logging.info(":) glmcloud: " + answer_total)
        logging.info("------------------------------------------------------")
        
        functions_name, functions_args = extract(answer_total)
        logging.info(":) function: " + str(functions_name) + str(functions_args))

        # only get the first function name, TODO
        if(len(functions_name) > 0):
            break
    
    functions_index = transfer(functions_name, functions_args)
    # logging.info(":) index: " + str(functions_index))

    return functions_index


apikey, prompt, prefix, suffix = asyncio.run(init())

client = ZhipuAI(api_key=apikey.decode('utf-8'))
logging.info(':) glm client init finished.')


# USER_ASK = "你听到有人问你<机器人摇摇头>，你应该怎么回应？如果你需要执行动作，请给出执行命令；如果你需要回答对方的提问，你可以将答案通过声卡播放。"

# # 1. get answer from glm cloud server
# answer = glmcloud.request(req.ask)
# logging.info(':) Glm Cloud Answer:' + answer)

# # 2. find functions in string
# functions_name, functions_args = glmcloud.extract(answer)
# logging.info(':) Glm Cloud Function:' + str(functions_name) + str(functions_args))

# # 3. execute functions
# functions_index = glmcloud.transfer(functions_name, functions_args)
# logging.info(':) Glm Cloud Function Index:' + str(functions_index))

# # 4. return answer and functions index
# print(answer, functions_index)


# test_str = "DIGITOPIA.voice_play('我的型号是射线巡游机，是由“数码大陆”公司设计制造。')"
# functions_name, functions_args = extract(test_str)
# logging.info(':) Glm Cloud Function:' + str(functions_name) + str(functions_args))

