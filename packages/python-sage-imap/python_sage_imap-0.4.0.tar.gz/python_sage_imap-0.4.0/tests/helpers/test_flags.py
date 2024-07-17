# test_enums.py
import pytest

from sage_imap.helpers.enums import FlagCommand, Flag


def test_flags_enum():
    assert Flag.SEEN == "\\Seen"
    assert Flag.ANSWERED == "\\Answered"
    assert Flag.FLAGGED == "\\Flagged"
    assert Flag.DELETED == "\\Deleted"
    assert Flag.DRAFT == "\\Draft"
    assert Flag.RECENT == "\\Recent"


def test_flag_command_enum():
    assert FlagCommand.ADD == "+FLAGS"
    assert FlagCommand.REMOVE == "-FLAGS"
