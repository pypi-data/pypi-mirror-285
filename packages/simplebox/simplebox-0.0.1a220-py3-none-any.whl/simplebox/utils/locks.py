#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Iterable
from contextlib import contextmanager
from multiprocessing import Manager
from multiprocessing.managers import ListProxy, BaseManager
from random import choice
from threading import RLock as TLock
from typing import TypeVar

from gevent.lock import RLock as CLock

from ..exceptions import NotFountException
from ..utils.objects import ObjectsUtils
from ..singleton import Singleton

T = TypeVar("T", TLock, CLock)


class Sentry(object):
    """
    Lock by variable.
    Theoretically, objects can be locked in this way.
    Duplicate elements are not added.
    For example, file locking.
    """

    def __init__(self, lock, free):
        ObjectsUtils.call_limit(__file__)
        self.lock: T = lock
        self.free = free

    def __str__(self):
        self.lock.acquire()
        try:
            return str(self.free)
        finally:
            self.lock.release()

    def __repr__(self):
        return self.__str__()

    def add(self, *obj):
        """
        add element(s)
        """
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.lock.acquire()
        try:
            for i in obj:
                if i not in self.free:
                    self.free.append(i)
        finally:
            self.lock.release()

    def add_item(self, item):
        """
        batch call add()
        """
        self.add(*item)

    @contextmanager
    def borrow(self, timeout=-1):
        """
        Select a random element from the queue.
        The element is not deleted.
        :return:
        """
        obj = None
        self.lock.acquire(timeout)
        try:
            size = len(self.free)
            if size > 0:
                obj = choice(self.free)
            yield obj
        finally:
            self.lock.release()

    @contextmanager
    def consume(self, value, null=True, timeout=-1):
        """
        When a specified element is consumed, it will be removed from the queue after the consumption is complete.
        :param timeout:
        :param value: Elements to be consumed.
        :param null: if not True, the element does not exist, an exception will be thrown.
        """
        obj = None
        self.lock.acquire(timeout=timeout)
        try:
            size = len(self.free)
            if size > 0:
                if value in self.free:
                    index = self.free.index(value)
                    obj = self.free.pop(index)
                else:
                    if null is not True:
                        raise NotFountException(f"not found element: {value}")
            yield obj
        finally:
            self.lock.release()


class ProcessLockManager(BaseManager):
    pass


class Locks(Singleton):
    """
    Built-in lock type
    """

    @staticmethod
    def process() -> Sentry:
        """
        multi processing lock
        """
        manager = Manager()
        free = manager.list()
        lock = manager.RLock()
        return Sentry(lock, free)

    @staticmethod
    def thread() -> Sentry:
        """
        multi thread lock
        """
        return Sentry(TLock(), [])

    @staticmethod
    def coroutine() -> Sentry:
        """
        coroutine lock
        """
        return Sentry(CLock(), [])


__all__ = [Locks, Sentry]
