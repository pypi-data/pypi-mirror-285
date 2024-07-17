# getconfigurationitem.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Read an item from a configuration file."""

import tkinter
import tkinter.messagebox


def get_configuration_item(configuration_file, item, default_values):
    """Return configuration value on file for item or builtin default.

    configuration_file   Name of configuration file.
    item                 Item in configuation file whose value is required.
    default_values       dict of default values for items.

    Return "" if configuration file cannot be opened or read, after showing
    a dialogue to tell the user.

    Return "" if the item exists but has no value.

    Return default value if the item does not exist and a default value exists.

    Return "" if the item does not exist and a default value does not exist.

    Return the item value if there is one.

    Items occupy a single line formatted as (?P<item>[^/s]*)/s*(?P<value>.*)

    """
    try:
        of = open(configuration_file)
        try:
            config_text = of.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=parent,
                message="".join(
                    (
                        "Unable to read from\n\n",
                        configuration_file,
                        "\n\n",
                        str(exc),
                        '\n\n"" will be returned as value of ',
                        item,
                    )
                ),
                title="Read File",
            )
            return ""
        finally:
            of.close()
    except Exception as exc:
        tkinter.messagebox.showinfo(
            parent=parent,
            message="".join(
                (
                    "Unable to open\n\n",
                    configuration_file,
                    "\n\n",
                    str(exc),
                    '\n\n"" will be returned as value of ',
                    item,
                )
            ),
            title="Open File",
        )
        return ""
    key = None
    for i in config_text.splitlines():
        i = i.split(maxsplit=1)
        if not i:
            continue
        if i[0].startswith("#"):
            continue
        if i[0] != item:
            continue
        key = item
        if len(i) == 1:
            value = ""
        else:
            value = i[1].strip()
    if key is None:
        for k, v in default_values:
            if k == item:
                key = item
                value = v
    if key is None:
        value = ""
    return value
