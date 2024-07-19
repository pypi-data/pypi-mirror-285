from typing import Callable as _Callable, Iterable as _Iterable, TypeVar as _TypeVar, Any as _Any
from concurrent import futures as _futures

_T = _TypeVar('_T')
_K = _TypeVar('_K')

class Parallel:
    """ A utility class for parallel execution of tasks using either threads or processes. """
    def __init__(self, maxWorkers = None, useProcesses=False):
        """
        :param useProcesses: Specify whether to use multiple processes (True) or threads (False).
            Note: for multiple processes it's recommended to use defined functions, since the new processes needs a way to access the method
        :param maxWorkers: The maximum number of workers to use for parallel execution. 
            * In multi processing defaults to cpu count 
            * in multi threading defaults to cpu count + 4
        """
        
        self._maxWorkers = maxWorkers
        self._useProcesses = useProcesses

    def _GetExecutor(self):
        return _futures.ProcessPoolExecutor(max_workers=self._maxWorkers) if self._useProcesses else _futures.ThreadPoolExecutor(max_workers=self._maxWorkers)
        
    def Invoke(self, *actions: _Callable[[None], _T]) -> list[_T]:
        with self._GetExecutor() as executor:
            promises = [executor.submit(action) for action in actions]
            done, not_done = _futures.wait(promises)
            results = [promise.result() for promise in promises] # get in correct order
            return results
        
    def InvokeAsync(self, *actions: _Callable[[None], _T]) -> list[_futures.Future[_T]]:
        executor = self._GetExecutor()
        promises = [executor.submit(action) for action in actions]
        executor.shutdown(wait=False, cancel_futures=False)
        return promises

    def ForEach(self, items:_Iterable[_T], itemAction:_Callable[[_T], _K]) -> list[_K]:
        with self._GetExecutor() as executor:
            promises = [executor.submit(itemAction, item) for item in items]
            done, not_done = _futures.wait(promises)
            results = [promise.result() for promise in promises] # get in correct order
            return results

    def ForEachAsync(self, items:_Iterable[_K], itemAction:_Callable[[_K], _T]) -> list[_futures.Future[_T]]:
        executor = self._GetExecutor()
        promises = [executor.submit(itemAction, item) for item in items]
        executor.shutdown(wait=False, cancel_futures=False)
        return promises
    


