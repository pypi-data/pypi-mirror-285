#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/12 下午7:34
@Author  : Gie
@File    : generate_mongo_ts.py
@Desc    :
"""
import time

import pymongo

import bson
import sys
import traceback
from datetime import datetime, timedelta

from hashlib import md5

from iaar_tools.iaarLog import IaarLoguru
from pymongo import MongoClient
from pytz import UTC

iaar_log = IaarLoguru()

"""
    注意：从1.1.0 以上版本，移除了部分功能，如需要请使用早期版本
    1.1.8 以上， 新入库数据与程序执行时时间间隔，小于 NEW_ADDING_INTERVAL 秒，则需要等待冷却后在处理
"""

NEW_ADDING_INTERVAL = 300


def make_md5(word):
    if not isinstance(type(word), str):
        word = str(word)
    return md5(word.encode('utf-8')).hexdigest()


def find_documents(conn, data_base, collection, query, projection, sort_key="_id", sort_value=pymongo.ASCENDING, limits=0):
    # 默认根据_id 升序排列，不限制返回的结果数量
    _docs = conn[data_base][collection].find(query, projection).sort(sort_key, sort_value).limit(limits)
    # 将结果集放到一个 list 中，方便计数
    return [item for item in _docs]


def wait_for_seconds(con, rounds, tracker):
    """

    Parameters
    ----------
    con     mongoClient
    rounds  需要等待的时间，每轮 20 秒
    tracker tracker

    Returns None
    -------

    """
    for ind in range(rounds):
        time.sleep(20)
        # 为了保持数据库连接不中断
        con.list_database_names()
        iaar_log.info(f'waited the {ind}th round').tracker(tracker)


def is_gt_end_id(end_id, latest_oid):
    """
    判断是否达到指定终点位置，然后退出程序
    :param end_id: 指定终点 id
    :param latest_oid: 遍历 mongo 过程中每批次的最后一条 id
    :return:
    """
    if end_id:
        real_end_oid = None
        if isinstance(end_id, str):
            real_end_oid = bson.ObjectId(end_id)
        elif isinstance(end_id, bson.ObjectId):
            real_end_oid = end_id

        if latest_oid > real_end_oid:
            return True


def continue_and_reset_exit_time(kws: dict, exit_time: datetime, need_set_exit_time: bool):
    """
    判断是否需要退出或者重置退出时间
    :param need_set_exit_time: 是否已经重置退出时间。如未重置，则需要重置。
                               该字段防止查不到数据时一直重置退出时间，导致无法退出。
    :param exit_time:     退出时间
    :param kws:
    :return: 重置后的退出时间 或者 None（ None 代表需要退出）
    """
    if kws and "not_exit_when_at_end" in kws.keys():
        # 当查询某个 MongoDB 达到终点，判断是否直接退出
        not_exit_when_at_end = kws.get("not_exit_when_at_end")
        # 当查询某个 MongoDB 达到终点，等待时间(单位分钟)
        wait_producer_minute = kws.get('wait_producer_minute')

        if not_exit_when_at_end and (exit_time > datetime.now()):
            if not need_set_exit_time:
                if wait_producer_minute:
                    assert isinstance(wait_producer_minute, int), "wait_producer_time need to be int(minute) type"
                    exit_time = datetime.now() + timedelta(minutes=wait_producer_minute)
                else:
                    exit_time = datetime.now() + timedelta(minutes=60)
            return exit_time
        return


def is_need_to_wait_for_new_data(oid):
    """
    当最新数据与当前时间戳间隔小于 NEW_ADDING_INTERVAL 秒时，认为在处理新增数据。为了避免 oid 精度问题，做延时等待处理
    Parameters
    ----------
    oid: 数据新一个 oid 时间戳和当前时间戳的差值小于指定值

    Returns boolean
    -------

    """
    return (datetime.now(tz=UTC) - oid.generation_time).total_seconds() < NEW_ADDING_INTERVAL


def generate_mongo_ts(uri, db, collection, more_filter, projections, core_logic, start_id='', end_id='', limits=1000, **kwargs):
    """

    :param uri: mongoDB 地址
    :param db: mongoDB 库名
    :param collection: mongoDB 表名
    :param more_filter: 其他 query
    :param projections: projection
    :param core_logic: 核心处理逻辑，调用方自行提供
    :param start_id: 自定义查询起点，必须是 MongoDB 的 ObjectId
    :param end_id: 自定义查询终点，必须是 MongoDB 的 ObjectId
    :param limits: 查询 MongoDB 的 limit
    :return:
    """
    query = {}
    track_id = ''
    latest_oid = ''  # ObjectId 类型
    exception_count = 0
    has_query_count = 1
    has_reset_exit_time = False
    exit_after_some_time = datetime(2099, 12, 31)

    if kwargs and kwargs.get('task_id'):
        track_id = kwargs.get("task_id")

    if isinstance(uri, str):
        conn = MongoClient(uri)
    elif isinstance(uri, pymongo.mongo_client.MongoClient):
        conn = uri
    else:
        iaar_log.error(f'uri 类型错误，系统退出。').tracker(track_id)
        sys.exit('uri 类型错误')

    if start_id:
        query = {"_id": {"$gte": bson.ObjectId(start_id)}}

    if more_filter:
        query.update(more_filter)

    while exception_count < 20:
        docs = find_documents(conn, db, collection, query, projections, "_id", pymongo.ASCENDING, limits)

        tracker = f'{track_id}-{make_md5(str(query))}'
        iaar_log.info(f"query {query}, raw docs size: {len(docs)} , query count: {has_query_count} ").tracker(tracker)

        try:
            if not docs:
                caret = continue_and_reset_exit_time(kwargs, exit_after_some_time, has_reset_exit_time)
                if not caret:
                    iaar_log.info(f"arrived at exit time point , exit! last oid is: {latest_oid} .").tracker(tracker)
                    return

                time.sleep(10)
                has_reset_exit_time = True
                exit_after_some_time = caret
                iaar_log.warning(f'query: {query}, the last oid : {latest_oid} , '
                                f'has reset new exit time: {exit_after_some_time}').tracker(tracker)
            else:
                # 重置退出标记
                has_reset_exit_time = False
                latest_oid = docs[-1].get("_id")

                # 最后一条数据距离当前时间间隔 NEW_ADDING_INTERVAL 秒内，不处理；
                if is_need_to_wait_for_new_data(latest_oid):
                    iaar_log.info(f'query: {query}, not process new adding data now, latest oid: {latest_oid} ').tracker(tracker)
                    wait_for_seconds(conn, 15, tracker)
                    continue

                # 是否大于指定的 end_id,
                # 1、不是：则不用理会继续进行。
                # 2、是的：则需要退出，只返回 end_id 之前的 docs
                if is_gt_end_id(end_id, latest_oid):
                    docs_tmp = []
                    for doc in docs:
                        latest_oid = doc.get('_id')
                        if is_gt_end_id(end_id, latest_oid):
                            break

                        docs_tmp.append(doc)
                    docs = docs_tmp

                has_query_count += 1
                query["_id"] = {"$gt": latest_oid}

                # 执行用户自定义的方法
                core_logic(conn, docs)
                iaar_log.info(f'core logic func had processed {len(docs)} docs, real '
                             f'start oid: {docs[0].get("_id")}, end oid: {docs[-1].get("_id")}').tracker(tracker)

                # 程序退出条件
                if is_gt_end_id(end_id, latest_oid):
                    iaar_log.info(f"Get end point, and mission is over! Last _id is: {end_id}.").tracker(tracker)
                    sys.exit()

        except Exception as e:
            query["_id"] = {"$gt": latest_oid}
            iaar_log.info(f'Get error, exception msg is {str(e) + ",trace:" + traceback.format_exc()}, latest oid is: {latest_oid}.').tracker(tracker)
            exception_count += 1

    iaar_log.info(f"Catch exception 20 times, mission is over. Last _id is: {latest_oid}.").tracker(track_id)
