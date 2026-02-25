import sys
import logging


FLEXUS_CUSTOM_LEVEL = logging.CRITICAL + 1
FLEXUS_CUSTOM_LEVEL_NAME = "FLEXUS_CUSTOM"


def flexus_alert(self, message, *args, **kwargs):
    if self.isEnabledFor(FLEXUS_CUSTOM_LEVEL):
        self._log(FLEXUS_CUSTOM_LEVEL, message, args, **kwargs)


def setup_logger():
    if getattr(logging.Logger, "falert", None):
        return
    logging.addLevelName(FLEXUS_CUSTOM_LEVEL, FLEXUS_CUSTOM_LEVEL_NAME)
    logging.Logger.falert = flexus_alert

    class CustomHandler(logging.Handler):
        def emit(self, record):
            level = "[INFO]"
            if record.levelno == logging.WARNING:
                level = "[WARN] ⚠️ "
            elif record.levelno in [logging.ERROR, logging.CRITICAL]:
                level = "[ERROR] 🛑"
            elif record.levelno == FLEXUS_CUSTOM_LEVEL:
                level = "[FLEXUS] 🚀 "
            log_entry = self.format(record)
            log_entry = log_entry.replace("!!LEVEL!!", level, 1)
            sys.stderr.write(log_entry)
            sys.stderr.write("\n")
            sys.stderr.flush()

    handler = CustomHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(name)s !!LEVEL!! %(message)s', datefmt='%Y%m%d %H:%M:%S'))

    for name in logging.Logger.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    gql_ws_logger = logging.getLogger("gql.transport.websockets")
    gql_ws_logger.handlers = []
    gql_ws_logger.propagate = False
    gql_ws_logger.setLevel(logging.WARNING)

    gql_ws_logger = logging.getLogger("gql.transport.aiohttp")
    gql_ws_logger.handlers = []
    gql_ws_logger.propagate = False
    gql_ws_logger.setLevel(logging.WARNING)
