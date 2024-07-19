#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
from simplebox.utils.objects import ObjectsUtils
class AsyncListener:
    def __init__(self):
        self.__status: bool = False

    def _set_task_status(self, status: bool):
        ObjectsUtils.call_limit(__file__)
        self.__status = status

    def get_task_status(self) -> bool:
        """
        Get async task run status. Requires the caller to actively poll for status
        """
        return self.__status

    def wait_task_status(self, timeout):
        """
        Proactively poll for task execution status, will block the process
        :param timeout: The polling timeout period, in seconds
        """
        start = datetime.datetime.now()
        while True:
            if (datetime.datetime.now() - start).seconds >= timeout or self.__status:
                break

from ._ticker import Ticker
from ._sched import Scheduler, SchedulerSync, SchedulerAsync, SchedulerSyncProcess, SchedulerAsyncProcess, \
    SchedulerAsyncIO, SchedulerGevent