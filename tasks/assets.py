import multiprocessing
import urllib.request
from pathlib import Path
from typing import Callable

from invoke import Collection as CollectionBase
from invoke import Task


class Collection(CollectionBase):

    def task(self, *args, **kwargs):
        def decor(func):
            self.add_task(Task(func, *args, **kwargs))
            return func

        return decor


class MultiprocessTask(Task):
    _tasks: list[Callable]

    def __init__(self, name: str):
        self._tasks = []
        super().__init__(self._handler, name = name)

    def add(self, func):
        self._tasks.append(func)
        return func

    def add_to_collection(self, coll: Collection):
        for task in self._tasks:
            coll.add_task(Task(task))
        coll.add_task(self)

    def _handler(self, c, **kwargs):
        for task in self._tasks:
            name = task.__name__
            if kwargs.get(name):
                multiprocessing.Process(target = task, args = (c,)).start()

    def argspec(self, body):
        spec_dict = {}

        for task in self._tasks:
            spec_dict[task.__name__] = True

        return list(spec_dict.keys()), spec_dict


def download_file(url: str, file_path: Path = Path("."), file_name: str = None):
    response = urllib.request.urlopen(url)
    data = response.read()

    if file_name is None:
        file_name = Path(url).name

    file = file_path / file_name

    file.write_bytes(data)
    print(f"{file} saved")
