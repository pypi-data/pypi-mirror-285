from typing import Tuple as _Tuple, Type as _Type, TypeAlias as _TypeAlias, Callable as _Callable
from types import TracebackType as _TracebackType
import unittest as _unittest
from enum import Enum as _Enum

class CaseOutcomeEnum(_Enum):
    Success = 0
    '''The test case passed without any issues.'''
    Fail = 1
    '''The test case failed due to an AssertionError.'''
    Error = 2
    '''The test case or test class raised an unexpected error.'''
    Skip = 3
    '''The test case was skipped, typically marked with @unittest.skip.'''
    UnexpectedSuccess = 4
    '''The test case was marked with @unittest.expectedFailure but unexpectedly succeeded.'''
    ExpectedFail = 5
    '''The test case was marked with @unittest.expectedFailure and failed as expected.'''

_TypeExcInfo:_TypeAlias = _Tuple[_Type[BaseException]|None, BaseException|None, _TracebackType|None]
class _CaseResult:

    def __init__(self,
            case: _unittest.TestCase, outcome:CaseOutcomeEnum, timeElapsed:float = 0,
            captured_stdout: str =None, captured_stderr: str = None,
            exception:_TypeExcInfo=None, exceptionString:str = None,
            skipReason:str=None):

        self.case = case
        '''The instantiated testcase, case.id() can be used get fully qualified name of test method'''
        self.outcome = outcome
        '''Indicates the specific type of case result'''
        self.timeElapsed = timeElapsed
        '''time taken for test case in seconds'''
        self.captured_stdout = captured_stdout
        self.captured_stderr = captured_stderr
        self.exception = exception
        '''The exception object tuple as given by sys.exc_info()'''
        self.exceptionString = exceptionString
        '''An highly detailed exception text, includes tracebacks and captured stdout/stderr'''
        self.skipReason=skipReason
        '''The reason for skipped test cases (if provided)'''
    
    @property
    def IsSuccess(self):
        """indicates if the test case as a whole is considered to be a success"""
        return self.outcome in (CaseOutcomeEnum.Success, CaseOutcomeEnum.Skip, CaseOutcomeEnum.ExpectedFail)

        
class _ArtifactTestResult(_unittest.TestResult):
    def __init__(self, afterCaseCallback:_Callable=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer = True
        self.timeElapsed:float = 0
        self._last_testCaseDuration:float = 0 #seconds
        
        self._afterCaseCallback = afterCaseCallback

        self._previousCase:_CaseResult = None

        #bad ones
        self.failures:list[_CaseResult] = []
        self.errors:list[_CaseResult] = []
        self.unexpectedSuccesses:list[_CaseResult] = []

        #mostly good ones
        self.skipped:list[_CaseResult] = []
        self.successes:list[_CaseResult] = []
        self.expectedFailures:list[_CaseResult] = []

    @property
    def allCaseResults(self):
        yield from self.failures
        yield from self.errors
        yield from self.unexpectedSuccesses

        yield from self.skipped
        yield from self.successes
        yield from self.expectedFailures

    def stopTest(self, test: _unittest.TestCase):
        super().stopTest(test)
        if(self._afterCaseCallback is not None):
            self._afterCaseCallback(self._previousCase)
        return

    def addSubTest(self, test, subtest, err):
        """
        Called at the end of a subtest.
        'err' is None if the subtest ended successfully, otherwise it's a tuple of values as returned by sys.exc_info().

        The saved caseobject will be if type unittest.case._SubTest which includes property test_case eg reference to parent testcase
        """

        self._mirrorOutput = True #stream writes inside of subtests should be reflected upwards

        if err is None:
            res = _CaseResult(
                case=subtest, outcome=CaseOutcomeEnum.Success, timeElapsed=self._last_testCaseDuration,
                captured_stdout=self._stdout_buffer.getvalue(), captured_stderr=self._stderr_buffer.getvalue()
            )
            self._previousCase = res
            self.successes.append(res)
        else:
            if getattr(self, 'failfast', False):
                self.stop()
            if issubclass(err[0], test.failureException):
                target, status = self.failures, CaseOutcomeEnum.Fail
            else:
                target, status = self.errors, CaseOutcomeEnum.Error
            res = _CaseResult(
                case=subtest, outcome=status, timeElapsed=self._last_testCaseDuration,
                captured_stdout=self._stdout_buffer.getvalue(), captured_stderr=self._stderr_buffer.getvalue(),
                exception=err, exceptionString=self._exc_info_to_string(err, test)
            )
            self._previousCase = res
            target.append(res)

    def addSuccess(self, test:_unittest.TestCase):
        res = _CaseResult(
            case=test, outcome=CaseOutcomeEnum.Success, timeElapsed=self._last_testCaseDuration,
            captured_stdout=self._stdout_buffer.getvalue(), captured_stderr=self._stderr_buffer.getvalue()
        )
        self._previousCase = res
        self.successes.append(res)

    @_unittest.result.failfast
    def addError(self, test:_unittest.TestCase, err:_TypeExcInfo):
        """
        Called when an unexpected error type has occurred in class/setup/case/cleanup.
        'err' is a tuple of values as returned by sys.exc_info().
        """

        res = _CaseResult(
            case=test, outcome=CaseOutcomeEnum.Error, timeElapsed=self._last_testCaseDuration,
            captured_stdout=self._stdout_buffer.getvalue(), captured_stderr=self._stderr_buffer.getvalue(),
            exception=err, exceptionString=self._exc_info_to_string(err, test)
        )
        self._previousCase = res
        self.errors.append(res)

    @_unittest.result.failfast
    def addFailure(self, test:_unittest.TestCase, err:_TypeExcInfo):
        """
        Called when an exception of type AssertionError has occurred in setup/case/cleanup.
        'err' is a tuple of values as returned by sys.exc_info()
        """

        res = _CaseResult(
            case=test, outcome=CaseOutcomeEnum.Fail, timeElapsed=self._last_testCaseDuration,
            captured_stdout=self._stdout_buffer.getvalue(), captured_stderr=self._stderr_buffer.getvalue(),
            exception=err, exceptionString=self._exc_info_to_string(err, test)
        )
        self._previousCase = res
        self.failures.append(res)

    def addSkip(self, test, reason):
        res = _CaseResult(
            case=test, outcome=CaseOutcomeEnum.Skip, timeElapsed=self._last_testCaseDuration,
            captured_stdout=self._stdout_buffer.getvalue(), captured_stderr=self._stderr_buffer.getvalue(),
            skipReason=reason
        )
        self._previousCase = res
        self.skipped.append(res)

    def addExpectedFailure(self, test, err):
        """Called when an expected failure/error occurred. 'err' is a tuple of values as returned by sys.exc_info()."""

        #marked as status success, since we expected this failure
        res = _CaseResult(
            case=test, outcome=CaseOutcomeEnum.ExpectedFail, timeElapsed=self._last_testCaseDuration,
            captured_stdout=self._stdout_buffer.getvalue(), captured_stderr=self._stderr_buffer.getvalue(),
            exception=err, exceptionString=self._exc_info_to_string(err, test)
        )
        self._previousCase = res
        self.expectedFailures.append(res)

    @_unittest.result.failfast
    def addUnexpectedSuccess(self, test):
        """Called when a test was expected to fail, but succeed."""

        #marked as fail success, since we expected a failure instead of success
        res = _CaseResult(
            case=test, outcome=CaseOutcomeEnum.UnexpectedSuccess, timeElapsed=self._last_testCaseDuration,
            captured_stdout=self._stdout_buffer.getvalue(), captured_stderr=self._stderr_buffer.getvalue(),
        )
        self._previousCase = res
        self.unexpectedSuccesses.append(res)

    def addDuration(self, test: _unittest.TestCase, elapsed: float):
        '''is always called after a testcase run (includes setup/cleanup) and before the AddSuccess etc methods'''
        self._last_testCaseDuration = elapsed

class ArtifactTestRunner:
    """Object oriented wrapper for standard unittest"""

    def Run(self, testSuite: _unittest.TestSuite, afterCaseCallback:_Callable[[_CaseResult], None]=None):
        import time

        result = _ArtifactTestResult(afterCaseCallback)
        _unittest.signals.registerResult(result)
        startTime = time.perf_counter()
        result.startTestRun()
        try:
            testSuite(result)
        finally:
            result.stopTestRun()
        stopTime = time.perf_counter()
        result.timeElapsed = stopTime - startTime
        return result
    

