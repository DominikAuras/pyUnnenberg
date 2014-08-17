#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, collections
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

class LazyLoggerAdapter(object):
    """
    An adapter for loggers which evaluates a callable passed as msg
    only if needed.
    """

    def __init__(self, logger):
        self.logger = logger
        
    def _log(self, level, msg, args, kwargs):
      if isinstance(msg, collections.Callable):
          msg = msg()
      self.logger._log(level, msg, args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, kwargs)

    def info(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(INFO):
            self._log(INFO, msg, args, kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, kwargs)

    warn = warning

    def error(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, kwargs)

    def exception(self, msg, *args, **kwargs):
        kwargs['exc_info'] = 1
        self.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, kwargs)

    fatal = critical
    
    def log(self, level, msg, *args, **kwargs):
        if not isinstance(level, int):
            if raiseExceptions:
                raise TypeError("level must be an integer")
            else:
                return
        if self.logger.isEnabledFor(level):
            self._log(level, msg, args, kwargs)
            
    def isEnabledFor(self, lvl):
        return self.logger.isEnabledFor(lvl)


if __name__ == '__main__':
  logger = logging.getLogger(__name__)
  adapter = LazyLoggerAdapter(logger)

  rootlogger = logging.getLogger('')
  
  ll = logging.ERROR
  
  rootlogger.setLevel(ll)
  ch = logging.StreamHandler()
  ch.setLevel(ll)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  rootlogger.addHandler(ch)

  def test(x):
    print("Called test()")
    return x

  adapter.critical(lambda:test("critical"))
  adapter.error(lambda:test("error"))
  adapter.warning(lambda:test("warning"))
  adapter.info(lambda:test("info"))
  adapter.debug(lambda:test("debug"))