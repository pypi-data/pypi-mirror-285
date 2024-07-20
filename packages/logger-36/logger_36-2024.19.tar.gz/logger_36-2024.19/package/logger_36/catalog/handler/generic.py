"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import logging as lggg
import typing as h

try:
    from logger_36.catalog.config.console_rich import DATE_TIME_COLOR
    from logger_36.catalog.handler.console_rich import HighlightedVersion
    from rich.console import Console as console_t
    from rich.console import ConsoleOptions as console_options_t
    from rich.markup import escape as EscapedForRich
    from rich.terminal_theme import DEFAULT_TERMINAL_THEME
except ModuleNotFoundError:
    console_t = console_options_t = EscapedForRich = DEFAULT_TERMINAL_THEME = None

from logger_36.constant.record import SHOW_W_RULE_ATTR
from logger_36.task.format.rule import Rule, RuleAsText
from logger_36.type.handler import handler_extension_t


class can_show_message_p(h.Protocol):
    def ShowMessage(self, message: str, /) -> None: ...


interface_h = can_show_message_p | h.Callable[[str], None]


@d.dataclass(slots=True, repr=False, eq=False)
class generic_handler_t(lggg.Handler):
    """
    alternating_lines:
    - Initial value:
        - 1: enabled for dark background
        - 2: enabled for light background
        - anything else: disabled
    - Runtime value: 0/1=do not/do highlight next time.
    """

    extension: handler_extension_t = d.field(init=False)
    console: console_t = None
    console_options: console_options_t = None
    FormattedLines: h.Callable[..., tuple[str, str | None]] = d.field(init=False)
    alternating_lines: int = 0
    background_is_light: bool = True
    ShowMessage: h.Callable[[str], None] = lambda _arg: None

    name: d.InitVar[str | None] = None
    level: d.InitVar[int] = lggg.NOTSET
    show_where: d.InitVar[bool] = True
    show_memory_usage: d.InitVar[bool] = False
    message_width: d.InitVar[int] = -1
    formatter: d.InitVar[lggg.Formatter | None] = None

    supports_html: d.InitVar[bool] = False
    should_record: d.InitVar[bool] = (False,)
    rich_kwargs: d.InitVar[dict[str, h.Any] | None] = None
    interface: d.InitVar[interface_h | None] = None  # Cannot be None actually.

    def __post_init__(
        self,
        name: str | None,
        level: int,
        show_where: bool,
        show_memory_usage: bool,
        message_width: int,
        formatter: lggg.Formatter | None,
        supports_html: bool,
        should_record: bool,
        rich_kwargs: dict[str, h.Any] | None,
        interface: interface_h | None,
    ) -> None:
        """"""
        lggg.Handler.__init__(self)

        self.extension = handler_extension_t(
            name=name,
            show_where=show_where,
            show_memory_usage=show_memory_usage,
            handler=self,
            level=level,
            message_width=message_width,
            formatter=formatter,
        )

        if supports_html and (console_t is not None):
            if rich_kwargs is None:
                rich_kwargs = {}
            self.console = console_t(
                highlight=False,
                force_terminal=True,
                record=should_record,
                **rich_kwargs,
            )
            self.console_options = self.console.options.update(
                overflow="ignore", no_wrap=True
            )

        self.FormattedLines = self.extension.FormattedLines
        if self.alternating_lines == 1:
            self.alternating_lines = 0
            self.background_is_light = False
        elif self.alternating_lines == 2:
            self.alternating_lines = 0
            self.background_is_light = True
        else:
            self.alternating_lines = -1

        self.ShowMessage = getattr(
            interface, can_show_message_p.ShowMessage.__name__, interface
        )

    def emit(self, record: lggg.LogRecord, /) -> None:
        """"""
        if self.console is None:
            if hasattr(record, SHOW_W_RULE_ATTR):
                message = RuleAsText(record.msg)
            else:
                message, _ = self.FormattedLines(record, should_join_lines=True)
        else:
            if hasattr(record, SHOW_W_RULE_ATTR):
                richer = Rule(record.msg, DATE_TIME_COLOR)
            else:
                first, next_s = self.FormattedLines(record, PreProcessed=EscapedForRich)
                should_highlight_back = self.alternating_lines == 1
                if self.alternating_lines >= 0:
                    self.alternating_lines = (self.alternating_lines + 1) % 2
                richer = HighlightedVersion(
                    self.console,
                    first,
                    next_s,
                    record.levelno,
                    should_highlight_back=should_highlight_back,
                    background_is_light=self.background_is_light,
                )
            segments = self.console.render(richer, options=self.console_options)

            # Inspired from the code of: rich.console.export_html.
            html_segments = []
            for text, style, _ in segments:
                if text == "\n":
                    html_segments.append("\n")
                else:
                    if style is not None:
                        style = style.get_html_style(DEFAULT_TERMINAL_THEME)
                        if (style is not None) and (style.__len__() > 0):
                            text = f'<span style="{style}">{text}</span>'
                    html_segments.append(text)
            if html_segments[-1] == "\n":
                html_segments = html_segments[:-1]

            # /!\ For some reason, the widget splits the message into lines, place each
            # line inside a pre tag, and set margin-bottom of the first and list lines
            # to 12px. This can be seen by printing self.contents.toHtml(). To avoid the
            # unwanted extra margins, margin-bottom is set to 0 below.
            message = (
                "<pre style='margin-bottom:0px'>" + "".join(html_segments) + "</pre>"
            )

        self.ShowMessage(message)


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
