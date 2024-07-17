# indexmap.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide the Segment class to manage a range of record numbers.

This module is obsolete given existence of core.recordset module in
solentware_base package, a sibling of solentware_misc.

It is an inverted list bitmap manager in DPT style.  The database interface
for DPT is available at www.solentware.co.uk.

"""

import pickle

MAPSIZE = 2040  # integers to represent DPT page size minus reserved bytes
INTEGERSIZE = 32  # 32 bit integers
SEGMENTSIZE = MAPSIZE * INTEGERSIZE  # DPT record numbers per segment
SEGMENTRANGE = list(range(SEGMENTSIZE))
BITMASK = [1 << x for x in range(INTEGERSIZE - 1)]
BITMASK.append(~sum(BITMASK))  # 1 << INTEGERSIZE gives +ve Long Integer
SEGMENTDELIMITER = chr(0)  # delimiter in <index><delimiter><segment>


class Segment:
    """Create list or bitmap of record numbers in a segment."""

    def __init__(self, segment, pickled=None, bitmap=False, values=None):
        """Create a set of record numbers.

        Convert to bitmap if len(set) greater than len(list) for bitmap.
        If pickled Segment instance passed use it to create self.values.
        If values passed then bitmap determines how self.values is created.
        Default is an empty set.
        The segment number must be specified.

        """
        self.segment = segment
        if pickled is not None:
            self.values = pickle.loads(pickled)
        elif bitmap:
            if values is None:
                self.values = [0] * MAPSIZE
            else:
                self.values = list(values)
        else:
            if values is None:
                self.values = set()
            else:
                self.values = set(values)
                if len(self.values) > MAPSIZE:
                    self.convert_to_bitmap()

    def add_record_number(self, number):
        """Add record number."""
        segment, number = divmod(number, SEGMENTSIZE)
        if segment != self.segment:
            return
        if isinstance(self.values, set):
            self.values.add(number)
            if len(self.values) > MAPSIZE:
                self.convert_to_bitmap()
        else:
            element, bit = divmod(number, INTEGERSIZE)
            self.values[element] |= BITMASK[bit]

    def convert_to_bitmap(self):
        """Convert segment to bitmap representation."""
        if isinstance(self.values, set):
            values = self.values
            self.values = [0] * MAPSIZE
            for i in values:
                element, bit = divmod(i, INTEGERSIZE)
                self.values[element] |= BITMASK[bit]

    def convert_to_set(self):
        """Convert segment to set representation."""
        if not isinstance(self.values, set):
            values = self.values
            self.values = set()
            for i in SEGMENTRANGE:
                element, bit = divmod(i, INTEGERSIZE)
                if values[element] & BITMASK[bit]:
                    self.values.add(i)

    def get_record_numbers(self):
        """Return sorted record number list for deferred update."""
        values = self.values
        segment = self.segment
        if isinstance(values, set):
            records = sorted([segment + j for j in values])
        else:
            records = []
            for i in SEGMENTRANGE:
                element, bit = divmod(i, INTEGERSIZE)
                if self.values[element] & BITMASK[bit]:
                    records.append(segment + i)
        return records

    def pickle_map(self):
        """Return record number set for use in dbm style value."""
        return pickle.dumps(self.values, pickle.HIGHEST_PROTOCOL)

    def remove_record_number(self, number, convert=False):
        """Remove record number."""
        segment, number = divmod(number, SEGMENTSIZE)
        if segment != self.segment:
            return
        if isinstance(self.values, set):
            self.values.remove(number)
        else:
            element, bit = divmod(number, INTEGERSIZE)
            self.values[element] &= ~BITMASK[bit]
            if convert:
                count = 0
                values = self.values
                for i in SEGMENTRANGE:
                    element, bit = divmod(i, INTEGERSIZE)
                    if values[element] & BITMASK[bit]:
                        count += 1
                if count < MAPSIZE:
                    self.convert_to_set()

    def encode_segment_number(self):
        """Return segment number for use in dbm style key."""
        return "".join((SEGMENTDELIMITER, str(self.segment)))
