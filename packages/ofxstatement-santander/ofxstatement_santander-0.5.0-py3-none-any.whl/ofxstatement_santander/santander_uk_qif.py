import logging
from decimal import Decimal
from typing import Dict, Optional, Iterable, Tuple
import html
import re

from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import StatementLine, generate_transaction_id, Currency

from ofxstatement_qif.plugin import QIFParser

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("SantanderUKQIF")


class SantanderUKQIFPlugin(Plugin):
    """Santander UK QIF file parser"""

    def get_parser(self, filename: str) -> "SantanderUKQIFParser":

        kwargs = {}

        if "day-first" in self.settings:
            kwargs["day_first"] = True

        if "separator" in self.settings:
            kwargs["separator"] = self.settings["separator"]

        if "encoding" in self.settings:
            kwargs["encoding"] = self.settings["encoding"]

        if "account" in self.settings:
            kwargs["account_name"] = self.settings["account"]

        if "currency" in self.settings:
            kwargs["currency"] = self.settings["currency"]

        return SantanderUKQIFParser(path=filename, **kwargs)


class SantanderUKQIFParser(StatementParser):
    """Santander UK QIF statement parser"""

    parser: QIFParser

    def __init__(
        self,
        path: str,
        separator: str = "\n",
        day_first: bool = False,
        encoding: str = "utf-8",
        account_name: str = "Quiffen Default Account",
        currency: Optional[str] = None,
    ) -> None:
        """Return a class instance of QIFParser

        Parameters
        ----------
        path : Union[FilePath, str]
            The path to the QIF file.
        separator : str, default='\n'
            The line separator for the QIF file. This probably won't need
            changing.
        day_first : bool, default=False
            Whether the day or month comes first in the date.
        encoding : str, default='utf-8'
            The encoding of the QIF file.
        account_name : str, default='Quiffen Default Account'
            The account name to extract transactions from.
        currency : Optional[str], default=None
            The currency used for the transactions.
        """
        super().__init__()

        self.parser = QIFParser(
            path, separator, day_first, encoding, account_name, currency
        )

    @staticmethod
    def get_transaction_memo(memo: Optional[str]) -> Optional[str]:
        if not memo:
            return None
        split_memo = re.split(r" , \d(.*)", memo)
        if len(split_memo) < 2:
            return None
        return html.unescape(split_memo[0].strip())

    def split_records(self) -> Iterable[StatementLine]:
        statement = self.parser.parse()
        return statement.lines

    def parse_record(self, line: StatementLine) -> Optional[StatementLine]:
        maybe_memo = self.get_transaction_memo(line.payee)

        if maybe_memo:
            line.memo = maybe_memo
            line.payee = None

        return line
