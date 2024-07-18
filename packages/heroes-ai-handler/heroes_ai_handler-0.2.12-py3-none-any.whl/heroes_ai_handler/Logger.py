import logging


class Logger(logging.Logger):
    def __init__(
            self,
            name: str,
            log_to_console: bool = True,
            **kwargs,
        ) -> None:
        '''
        This class will create a logger with given settings.
        '''
        logging_library = super()
        logging_library.__init__(name, **kwargs)

        # Create logger
        self.logger = logging_library
        
        # Configure logging settings
        logger_formatter = self.CustomFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        if log_to_console:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logger_formatter)
            self.logger.addHandler(consoleHandler)



    class CustomFormatter(logging.Formatter):
        def __init__(self, fmt=None, datefmt=None, style='%'):
            super().__init__(fmt, datefmt, style)
            self.fmt = fmt
            self.datefmt = datefmt

        def format(self, record):
            record.asctime = self.formatTime(record, self.datefmt)
            record.name = record.name.ljust(21)
            record.levelname = record.levelname.ljust(8)
            return super().format(record)

