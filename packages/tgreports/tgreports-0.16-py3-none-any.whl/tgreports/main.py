"""
Reports functionality
"""

import json
import inspect
import traceback
import logging
import logging.config
from os.path import exists
from pathlib import Path

from tgio import Telegram


SYMBOLS = ["💬", "🟢", "⚠️", "❗️", "‼️", "✅", "🛎"]
TYPES = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "IMPORTANT",
    "REQUEST",
]


# pylint: disable=invalid-name
if exists("log.conf"):
    log_file = "log.conf"
else:
    log_file = Path(__file__).parent / "log.conf"
logging.config.fileConfig(log_file)
logger_err = logging.getLogger(__name__)
logger_log = logging.getLogger("info")


def to_json(data):
    """Convert any type to json serializable object"""

    if isinstance(data, str):
        return data

    try:
        return json.dumps(data, ensure_ascii=False)
    except TypeError:
        return str(data)


def dump(data):
    """json.dumps() with errors handler"""

    if data is None:
        return None

    if not isinstance(data, dict):
        return str(data)

    return {k: to_json(v) for k, v in data.items() if v is not None}


class Report:
    """Report logs and notifications on Telegram chat or in log files"""

    def __init__(self, mode, token, bug_chat):
        self.mode = mode or "TEST"
        self.tg = Telegram(token)
        self.bug_chat = bug_chat

    # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    async def _report(
        self,
        text,
        type_=1,
        extra=None,
        tags=None,
        error=None,
    ):
        """Make report message and send"""

        without_traceback = type_ in (1, 5, 6)

        if isinstance(extra, dict):
            if extra.get("name") == "Error":
                type_ = 3
                del extra["name"]

            if extra.get("title") == "Error":
                type_ = 3
                del extra["title"]

        if self.mode not in ("PRE", "PROD") and type_ == 1:
            return

        if not tags:
            tags = []

        if without_traceback:
            filename = None
            lineno = None
            function = None

        elif error:
            traces = traceback.extract_tb(error.__traceback__)[::-1]

            for trace in traces:
                if "python" not in trace.filename:
                    break
            else:
                trace = traces[0]

            filename = trace.filename
            lineno = trace.lineno
            function = trace.name

        else:
            previous = inspect.stack()[2]
            filename = previous.filename
            lineno = previous.lineno
            function = previous.function

        if filename:
            if filename[:4] == "/app":
                filename = filename[4:]
            if filename[:3] == "/./":
                filename = filename[3:]

            path = filename.replace("/", ".").split(".")[:-1]

            if path:
                if path[0] == "api":
                    path = path[1:]

                if function and function != "handle":
                    path.append(function)

                path = "\n" + ".".join(path)

            else:
                path = ""

            source = f"\n{filename}:{lineno}"

        else:
            path = ""
            source = ""

        text = f"{SYMBOLS[type_]} {self.mode} {TYPES[type_]}" f"{path}" f"\n\n{text}"

        if extra:
            if isinstance(extra, dict):
                extra_text = "\n".join(f"{k} = {v}" for k, v in extra.items())
            else:
                extra_text = str(extra)

            text_with_extra = text + "\n\n" + extra_text
        else:
            text_with_extra = text

        tags = [self.mode.lower()] + tags

        outro = f"\n{source}" f"\n#" + " #".join(tags)

        text += outro
        text_with_extra += outro

        try:
            await self.tg.send(self.bug_chat, text_with_extra, markup=None)

        # pylint: disable=broad-except
        except Exception as e:
            if extra:
                logger_err.error(
                    "%s  Send report  %s %s",
                    SYMBOLS[3],
                    extra,
                    e,
                )

                try:
                    await self.tg.send(self.bug_chat, text, markup=None)

                # pylint: disable=broad-except,redefined-outer-name
                except Exception as e:
                    logger_err.error(
                        "%s  Send report  %s %s %s",
                        SYMBOLS[3],
                        type_,
                        text,
                        e,
                    )

            else:
                logger_err.error(
                    "%s  Send report  %s %s %s",
                    SYMBOLS[3],
                    type_,
                    text,
                    e,
                )

    @staticmethod
    async def debug(text, extra=None):
        """Debug
        Sequence of function calls, internal values
        """

        logger_log.debug("%s  %s  %s", SYMBOLS[0], text, dump(extra))

    async def info(self, text, extra=None, tags=None, silent=False):
        """Info
        System logs and event journal
        """

        extra = dump(extra)
        logger_log.info(
            "%s  %s  %s",
            SYMBOLS[1],
            text,
            json.dumps(extra, ensure_ascii=False),
        )

        if not silent:
            await self._report(text, 1, extra, tags)

    async def warning(
        self,
        text,
        extra=None,
        tags=None,
        error=None,
        silent=False,
    ):
        """Warning
        Unexpected / strange code behavior that does not entail consequences
        """

        extra = dump(extra)
        logger_err.warning(
            "%s  %s  %s",
            SYMBOLS[2],
            text,
            json.dumps(extra, ensure_ascii=False),
        )

        if not silent:
            await self._report(text, 2, extra, tags, error)

    async def error(
        self,
        text,
        extra=None,
        tags=None,
        error=None,
        silent=False,
    ):
        """Error
        An unhandled error occurred
        """

        extra = dump(extra)
        content = (
            "".join(traceback.format_exception(None, error, error.__traceback__))
            if error is not None
            else f"{text}  {json.dumps(extra, ensure_ascii=False)}"
        )
        logger_err.error("%s  %s", SYMBOLS[3], content)

        if not silent:
            await self._report(text, 3, extra, tags, error)

    async def critical(
        self,
        text,
        extra=None,
        tags=None,
        error=None,
        silent=False,
    ):
        """Critical
        An error occurred that affects the operation of the service
        """

        extra = dump(extra)
        content = (
            "".join(traceback.format_exception(None, error, error.__traceback__))
            if error is not None
            else f"{text}  {json.dumps(extra, ensure_ascii=False)}"
        )
        logger_err.critical("%s  %s", SYMBOLS[4], content)

        if not silent:
            await self._report(text, 4, extra, tags, error)

    async def important(self, text, extra=None, tags=None, silent=False):
        """Important
        Trigger on tracked user action was fired
        """

        extra = dump(extra)
        logger_log.info(
            "%s  %s  %s",
            SYMBOLS[5],
            text,
            json.dumps(extra, ensure_ascii=False),
        )

        if not silent:
            await self._report(text, 5, extra, tags)

    async def request(self, text, extra=None, tags=None, silent=False):
        """Request
        The user made a request, the intervention of administrators is necessary
        """

        extra = dump(extra)
        logger_log.info(
            "%s  %s  %s",
            SYMBOLS[6],
            text,
            json.dumps(extra, ensure_ascii=False),
        )

        if not silent:
            await self._report(text, 6, extra, tags)
