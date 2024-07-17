# utilities.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""This module provides classes for handling dates and names."""

import re
import datetime
import calendar

# AppSysPersonName constants
NSPACE = " "
NCOMMA = ","
NDOT = "."
NHYPHEN = "-"
NAMEDELIMITER = "".join((NSPACE, NCOMMA, NDOT))
NAMEHYPHENED = "".join((NHYPHEN,))


class AppSysDate:
    """Date parser that accepts various common formats.

    wx.DateTime was used to do these things prior to switch to Tkinter.

    The method names in use then, and their signatures, are retained.

    """

    ymd_re = re.compile(
        "".join(
            (
                r"(\s*)",
                r"([0-9]+|[a-zA-Z]+)",
                r"(\s+|\.|/|-)",
                r"([0-9]+|[a-zA-Z]+)",
                r"(\s+|\.|/|-)",
                r"([0-9]+)",
                r"(\s+.*|\Z)",
            )
        )
    )
    md_re = re.compile(
        "".join(
            (
                r"(\s*)",
                r"([0-9]+|[a-zA-Z]+)",
                r"(\s+|\.|/|-)",
                r"([0-9]+|[a-zA-Z]+)",
                r"(\s+.*|\Z)",
            )
        )
    )

    date_formats = (
        "%d %b %Y",  # 30 Nov 2006
        "%b %d %Y",  # Nov 30 2006
        "%d %B %Y",  # 30 November 2006
        "%B %d %Y",  # November 30 2006
        "%d %b %y",  # 30 Nov 06
        "%b %d %y",  # Nov 30 06
        "%d %B %y",  # 30 November 06
        "%B %d %y",  # November 30 06
        "%d.%m.%Y",  # 30.11.2006
        "%d.%m.%y",  # 30.11.06
        "%m.%d.%Y",  # 11.30.2006
        "%m.%d.%y",  # 11.30.06
        "%Y-%m-%d",  # 2006-11-30
        "%Y/%m/%d",  # 2006/11/30
        "%y-%m-%d",  # 06-11-30
        "%d/%m/%Y",  # 30/11/2006
        "%d/%m/%y",  # 30/11/06
        "%m/%d/%Y",  # 11/30/2006
        "%m/%d/%y",  # 11/30/06
    )

    calendar = calendar

    def __init__(self):
        """Initialize data attributes."""
        self.date = None
        self.re_match = None
        self._bytes_input = None

    def iso_format_date(self):
        """Return ISO format date like 2007-08-26."""
        try:
            if self._bytes_input:
                return self.date.isoformat(" ").split()[0].encode("utf8")
            return self.date.isoformat(" ").split()[0]
        except AttributeError:
            return None

    def get_current_year(self):
        """Return current year."""
        return datetime.datetime.now().year

    def get_month_name(self, month):
        """Return abbreviated month name.

        Month is in range 0-11 following wx.DateTime convention.

        """
        if month > 11:
            month = -1
        elif month < 0:
            month = -1
        return self.calendar.month_abbr[month + 1]

    def length_date_string(self):
        """Return number of characters interpreted as date by parse_date."""
        if self.re_match is not None:
            groups = self.re_match.groups()
            if self._bytes_input:
                if len(groups) > 5:
                    return len("".join(groups[:6]).encode("utf8"))
                return len("".join(groups[:4]).encode("utf8"))
            if len(groups) > 5:
                return len("".join(groups[:6]))
            return len("".join(groups[:4]))

        return -1

    def parse_date(self, date, assume_current_year=False):
        """Return valid date at start of date argument.

        Date formats are tried in their order in the date_formats attribute
        with the 'day month year' interpretation taking precedence over
        'month day year' where the date is ambiguous like '10/11/12'.

        wx.DateTime.ParseDate returns -1 for conversion failure rather than
        None as might be expected from documentation (which says NULL). So
        do this as existing callers expect it.

        """
        if isinstance(date, bytes):
            self._bytes_input = True
            date = date.decode("utf8")
        self.re_match = self.ymd_re.match(date)
        if self.re_match is None:
            if not assume_current_year:
                return -1
            self.re_match = self.md_re.match(date)
            if self.re_match is None:
                self.date = None
                return -1

        groups = self.re_match.groups()
        if len(groups) > 5:
            datestring = "".join(groups[1:6])
        else:
            datestring = "".join(
                (
                    "".join((groups[1:4])),
                    groups[2],
                    str(datetime.datetime.now().year),
                )
            )

        for format_ in self.date_formats:
            try:
                self.date = datetime.datetime.strptime(datestring, format_)
                return self.length_date_string()
            except ValueError:
                pass

        return -1


class AppSysPersonName:
    """Name parser that picks out surname and forenames.

    Instances provide three attributes: name, surname, and forenames.  Name
    is the concatenation of surname and forenames separated by one space.

    Commas and full-stops are removed from the name passed as argument when
    creating the instance.  The attribute _name retains the passed value.

    The passed value may be str or bytes but the other attributes are str,
    using decode('utf8') if necessary to convert bytes to str.
    """

    def __init__(self, name):
        """Split name into surname and forenames.

        The text before the first comma in a name is the surname and the
        text after the comma is the forenames.  Without a comma a word
        longer than one character is chosen as the surname in order from:
        last word in name; first word in name; latest word in name.  If all
        words are one character the last word is the surname.

        Words are delimited by space comma and dot.

        """
        self._name = name
        if isinstance(name, bytes):
            name = name.decode("utf8")
        self.name = None
        self.surname = ""
        self.forenames = None
        partialnames = []
        commasplit = name.split(NCOMMA, 1)
        if len(commasplit) > 1:
            surname, name = commasplit
            self.surname = NSPACE.join(surname.split())
        partial = []
        for char in name:
            if char in NAMEDELIMITER:
                partialnames.append("".join(partial))
                partial = []
            else:
                partial.append(char)
        if partial:
            partialnames.append("".join(partial))
        partialnames = NSPACE.join(partialnames).split()
        if partialnames and not self.surname:
            surname = partialnames.pop()
            if len(surname) < 2:
                partialnames.append(surname)
                surname = partialnames.pop(0)
                if len(surname) < 2:
                    partialnames.insert(0, surname)
                    index = -1
                    for i, word in enumerate(partialnames):
                        if len(word) > 1:
                            index = i
                    surname = partialnames.pop(index)
            self.surname = surname
        self.forenames = NSPACE.join(partialnames)
        self.name = NSPACE.join((self.surname, self.forenames))
        if isinstance(self._name, bytes):
            self.surname = self.surname.encode("utf8")
            self.forenames = self.forenames.encode("utf8")
            self.name = self.name.encode("utf8")


class AppSysPersonNameParts(AppSysPersonName):
    """Name parser that picks out surname forenames and all partial names.

    Instances add the attribute partialnames to those provided by the
    superclass.  Partialnames is the set of all partial names.

    """

    def __init__(self, name):
        """Parser to pick out surname, forenames, and all partial names.

        The superclass picks out surname and forenames.

        The surname becomes a partial name.  The words formed by splitting
        surname and forenames at whitespace become partial names and these
        words split by hyphens become partial names.

        """
        super().__init__(name)
        name = self.name
        if isinstance(name, bytes):
            name = name.decode("utf8")
        partialnames = name.split()
        self.partialnames = set(partialnames)
        for joiner in NAMEHYPHENED:
            if name.find(joiner) > -1:
                for word in partialnames:
                    partial = []
                    for char in word:
                        if char in NAMEHYPHENED:
                            partial = "".join(partial)
                            if partial:
                                self.partialnames.add("".join(partial))
                            partial = []
                        else:
                            partial.append(char)
                    if partial:
                        self.partialnames.add("".join(partial))
                break
        if isinstance(self._name, bytes):
            self.partialnames = {pn.encode("utf8") for pn in self.partialnames}
        self.partialnames.add(self.surname)
