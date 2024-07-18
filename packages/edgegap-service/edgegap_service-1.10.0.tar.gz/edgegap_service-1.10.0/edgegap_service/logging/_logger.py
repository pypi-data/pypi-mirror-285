import http
import logging
from copy import copy

from edgegap_logging import Color, DefaultFormatter, Format


class AccessFormatter(DefaultFormatter):
    status_code_colours = {
        1: Color.WHITE,
        2: Color.GREEN,
        3: Color.YELLOW,
        4: Color.LIGHTRED_EX,
        5: Color.RED,
    }

    default_fmt = '%(asctime)s | %(levelname)s | %(name)s | %(client_addr)s - [%(request_line)s] %(status_code)s'

    def get_status_code(self, status_code: int) -> str:
        try:
            status_phrase = http.HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = ''

        status_and_phrase = f'{status_code} {status_phrase}'

        if self.use_colors:
            color = self.status_code_colours.get(status_code // 100)

            return Format.color(status_phrase, color)

        return status_and_phrase

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)

        (
            client_addr,
            method,
            full_path,
            http_version,
            status_code,
        ) = record_copy.args  # type: ignore[misc]
        status_code = self.get_status_code(int(status_code))  # type: ignore[arg-type]
        request_line = f'{method} {full_path} HTTP/{http_version}'

        if self.use_colors:
            request_line = Format.color(request_line, bold=True)

        record_copy.__dict__.update(
            {
                'client_addr': client_addr,
                'request_line': request_line,
                'status_code': status_code,
            },
        )
        return super().formatMessage(record_copy)
