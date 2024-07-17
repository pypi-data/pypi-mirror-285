# null.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide a null object which does nothing.

This module is the placeholder object copied from Python Cookbook 2nd
edition 6.17.

"""


class Null:
    """Null objects always and reliably 'do nothing'."""

    # one instance per subclass optimization
    def __new__(cls, *args, **kwargs):
        """Return cls._inst after creating it if it does not exist."""
        if "_inst" not in vars(cls):
            cls._inst = object.__new__(cls, *args, **kwargs)
        return cls._inst

    def __init__(self, *args, **kwargs):
        """Do nothing."""

    def __call__(self, *args, **kwargs):
        """Return self."""
        return self

    def __repr__(self):
        """Return "Null()"."""
        return "Null()"

    def __bool__(self):
        """Return False."""
        return False

    def __getattr__(self, name):
        """Return self."""
        return self

    def __setattr__(self, name, value):
        """Return self."""
        return self

    def __delattr__(self, name):
        """Return self."""
        return self
