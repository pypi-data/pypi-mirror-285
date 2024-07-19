from mrkutil.communication import listen
from mrkutil.logging import get_logging_config
from package.app import handlers, settings  # noqa importing handlers

import os
import sys
import logging
import logging.config


logging.config.dictConfig(
    get_logging_config(settings.LOG_LEVEL, settings.JSON_FORMAT, False)
)

logger = logging.getLogger("main")


def main():
    """
    App starting point
    """
    try:
        pid = str(os.getpid())
        if not os.path.isdir("/tmp/service"):
            os.makedirs("/tmp/service")
        pidfile = "/tmp/service_{{ cookiecutter.project_name }}.pid"
        if os.path.isfile(pidfile):
            logger.warning("Service is already running")
            sys.exit(1)
        with open(pidfile, "w") as file:
            file.write(pid)
            file.write("\n")
        try:
            logger.info("Starting ...")
            listen(
                exchange=settings.EXCHANGE_{{ cookiecutter.project_name.upper() }},
                exchange_type=settings.EXCHANGE_TYPE_{{ cookiecutter.project_name.upper() }},
                queue=settings.QUEUE_{{ cookiecutter.project_name.upper() }},
            )
            sys.exit(0)
        finally:
            os.unlink(pidfile)
    except KeyboardInterrupt:
        logger.info("Reloading ...")


if __name__ == "__main__":
    if settings.DEVELOP:
        from watchfiles import run_process

        logger.info("Running watchfiles, will watch for changes in current service ...")
        run_process("./package", target=main)
    else:
        main()
