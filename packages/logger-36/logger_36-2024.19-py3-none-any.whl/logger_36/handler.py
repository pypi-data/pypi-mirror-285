"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import logging as lggg
import sys as sstm
from pathlib import Path as path_t

from logger_36.catalog.handler.console import console_handler_t
from logger_36.catalog.handler.file import file_handler_t
from logger_36.catalog.handler.generic import generic_handler_t, interface_h
from logger_36.constant.error import MISSING_RICH_ERROR
from logger_36.instance.logger import LOGGER

try:
    from logger_36.catalog.handler.console_rich import console_rich_handler_t

    _MISSING_RICH_ERROR = None
except ModuleNotFoundError:
    from logger_36.catalog.handler.console import (
        console_handler_t as console_rich_handler_t,
    )

    _MISSING_RICH_ERROR = MISSING_RICH_ERROR


def AddGenericHandler(
    interface: interface_h,
    /,
    *,
    logger: lggg.Logger | None = None,
    name: str | None = None,
    level: int = lggg.INFO,
    show_where: bool = True,
    show_memory_usage: bool = False,
    message_width: int = -1,
    formatter: lggg.Formatter | None = None,
    supports_html: bool = False,
    alternating_lines: int = 2,
    should_record: bool = False,
    should_hold_messages: bool = False,
    **kwargs,
) -> None:
    """"""
    if logger is None:
        logger = LOGGER

    handler = generic_handler_t(
        name=name,
        level=level,
        show_where=show_where,
        show_memory_usage=show_memory_usage,
        message_width=message_width,
        formatter=formatter,
        supports_html=supports_html,
        alternating_lines=alternating_lines,
        should_record=should_record,
        rich_kwargs=kwargs,
        interface=interface,
    )
    logger.AddHandler(handler, should_hold_messages)


def AddConsoleHandler(
    *,
    logger: lggg.Logger | None = None,
    name: str | None = None,
    level: int = lggg.INFO,
    show_where: bool = True,
    show_memory_usage: bool = False,
    message_width: int = -1,
    formatter: lggg.Formatter | None = None,
    should_hold_messages: bool = False,
) -> None:
    """"""
    if logger is None:
        logger = LOGGER

    handler = console_handler_t(
        name=name,
        level=level,
        show_where=show_where,
        show_memory_usage=show_memory_usage,
        message_width=message_width,
        formatter=formatter,
    )
    logger.AddHandler(handler, should_hold_messages)


def AddRichConsoleHandler(
    *,
    logger: lggg.Logger | None = None,
    name: str | None = None,
    level: int = lggg.INFO,
    show_where: bool = True,
    show_memory_usage: bool = False,
    message_width: int = -1,
    formatter: lggg.Formatter | None = None,
    alternating_lines: int = 2,
    should_hold_messages: bool = False,
    should_install_traceback: bool = False,
    should_record: bool = False,
    **kwargs,
) -> None:
    """"""
    global _MISSING_RICH_ERROR
    if _MISSING_RICH_ERROR is not None:
        print(_MISSING_RICH_ERROR, file=sstm.stderr)
        _MISSING_RICH_ERROR = None

    if logger is None:
        logger = LOGGER

    if console_rich_handler_t is console_handler_t:
        additional_s = {}
    else:
        additional_s = {
            "alternating_lines": alternating_lines,
            "should_install_traceback": should_install_traceback,
            "should_record": should_record,
            "rich_kwargs": kwargs,
        }
    handler = console_rich_handler_t(
        name=name,
        level=level,
        show_where=show_where,
        show_memory_usage=show_memory_usage,
        message_width=message_width,
        formatter=formatter,
        **additional_s,
    )
    logger.AddHandler(handler, should_hold_messages)


def AddFileHandler(
    path: str | path_t,
    /,
    *args,
    logger: lggg.Logger | None = None,
    name: str | None = None,
    level: int = lggg.INFO,
    show_where: bool = True,
    show_memory_usage: bool = False,
    message_width: int = -1,
    formatter: lggg.Formatter | None = None,
    should_hold_messages: bool = False,
    **kwargs,
) -> None:
    """"""
    if isinstance(path, str):
        path = path_t(path)
    if path.exists():
        raise ValueError(f"File or folder already exists: {path}.")
    if logger is None:
        logger = LOGGER

    handler = file_handler_t(
        name=name,
        level=level,
        show_where=show_where,
        show_memory_usage=show_memory_usage,
        message_width=message_width,
        formatter=formatter,
        path=path,
        handler_args=args,
        handler_kwargs=kwargs,
    )
    logger.AddHandler(handler, should_hold_messages)


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
