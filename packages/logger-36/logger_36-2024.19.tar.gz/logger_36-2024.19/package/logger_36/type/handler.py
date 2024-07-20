"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import logging as lggg
import sys as sstm
import typing as h
from os import sep as FOLDER_SEPARATOR
from pathlib import Path as path_t

from logger_36.config.message import TIME_FORMAT, WHERE_FORMAT
from logger_36.constant.error import MEMORY_MEASURE_ERROR
from logger_36.constant.handler import HANDLER_CODES
from logger_36.constant.message import NEXT_LINE_PROLOGUE
from logger_36.constant.record import HIDE_WHERE_ATTR, SHOW_WHERE_ATTR
from logger_36.task.format.message import FormattedMessage, MessageFormat
from logger_36.task.measure.chronos import TimeStamp
from logger_36.task.measure.memory import CanCheckUsage as CanCheckMemoryUsage

_MEMORY_MEASURE_ERROR = MEMORY_MEASURE_ERROR


@d.dataclass(slots=True, repr=False, eq=False)
class handler_extension_t:
    name: str | None = None
    show_where: bool = True
    show_memory_usage: bool = False
    message_width: int = -1
    FormattedRecord: h.Callable[[lggg.LogRecord], str] = d.field(init=False)

    handler: d.InitVar[lggg.Handler | None] = None
    level: d.InitVar[int] = lggg.NOTSET
    formatter: d.InitVar[lggg.Formatter | None] = None

    def __post_init__(
        self, handler: lggg.Handler | None, level: int, formatter: lggg.Formatter | None
    ) -> None:
        """"""
        global _MEMORY_MEASURE_ERROR

        if self.name in HANDLER_CODES:
            raise ValueError(
                FormattedMessage(
                    "Invalid handler name",
                    actual=self.name,
                    expected=f"a name not in {str(HANDLER_CODES)[1:-1]}",
                )
            )

        if self.name is None:
            self.name = TimeStamp()

        if self.show_memory_usage and not CanCheckMemoryUsage():
            self.show_memory_usage = False
            if _MEMORY_MEASURE_ERROR is not None:
                print(_MEMORY_MEASURE_ERROR, file=sstm.stderr)
                _MEMORY_MEASURE_ERROR = None

        handler.setLevel(level)

        if 0 < self.message_width < 5:
            self.message_width = 5
        if formatter is None:
            message_format = MessageFormat(self.show_where, self.show_memory_usage)
            formatter = lggg.Formatter(fmt=message_format, datefmt=TIME_FORMAT)
        handler.setFormatter(formatter)
        self.FormattedRecord = handler.formatter.format

    def FormattedLines(
        self,
        record: lggg.LogRecord,
        /,
        *,
        PreProcessed: h.Callable[[str], str] | None = None,
        should_join_lines: bool = False,
    ) -> tuple[str, str | None]:
        """
        See logger_36.catalog.handler.README.txt.
        """
        record.level_first_letter = record.levelname[0]

        message = record.msg
        if not isinstance(message, str):
            message = str(message)
        original_message = message

        if PreProcessed is not None:
            message = PreProcessed(message)
        if (has_newlines := ("\n" in message)) or (
            (self.message_width > 0) and (message.__len__() > self.message_width)
        ):
            if has_newlines:
                lines = message.splitlines()
                if self.message_width > 0:
                    lines = _WrappedLines(lines, self.message_width)
            else:
                lines = _WrappedLines([message], self.message_width)
            next_lines = NEXT_LINE_PROLOGUE.join(lines[1:])
            next_lines = f"{NEXT_LINE_PROLOGUE}{next_lines}"
            message = lines[0]
        else:
            next_lines = None
        if self.message_width > 0:
            n_missing_s = self.message_width - message.__len__()
            if n_missing_s > 3:
                message += " " + (n_missing_s - 1) * "."
            elif n_missing_s > 0:
                message += n_missing_s * " "

        record.msg = message
        if self.show_where and not hasattr(record, SHOW_WHERE_ATTR):
            hide_where = getattr(record, HIDE_WHERE_ATTR, False)
            if hide_where:
                record.where = ""
            else:
                module = path_t(record.pathname)
                path_was_found = False
                for path in sstm.path:
                    if module.is_relative_to(path):
                        module = module.relative_to(path)
                        path_was_found = True
                        break
                if path_was_found:
                    module = str(module.parent / module.stem)
                    module = module.replace(FOLDER_SEPARATOR, ".")
                else:
                    module = record.module
                record.where = WHERE_FORMAT.format(
                    module=module, funcName=record.funcName, lineno=record.lineno
                )
        first_line = self.FormattedRecord(record).replace("\t", " ")

        # Revert the record message to its original value for subsequent handlers.
        record.msg = original_message

        if should_join_lines:
            if next_lines is None:
                return first_line, None
            else:
                return f"{first_line}{next_lines}", None
        else:
            return first_line, next_lines


def _WrappedLines(lines: list[str], message_width: int, /) -> list[str]:
    """"""
    output = []

    for line in lines:
        while line.__len__() > message_width:
            if all(
                _elm != " " for _elm in line[(message_width - 1) : (message_width + 1)]
            ):
                if line[message_width - 2] == " ":
                    piece, line = (
                        line[: (message_width - 2)].rstrip(),
                        line[(message_width - 1) :],
                    )
                else:
                    piece, line = (
                        line[: (message_width - 1)] + "-",
                        line[(message_width - 1) :],
                    )
            else:
                piece, line = (
                    line[:message_width].rstrip(),
                    line[message_width:].lstrip(),
                )
            output.append(piece)

        output.append(line)

    return output


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
