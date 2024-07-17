# test_imap_message.py
import pytest

from sage_imap.models.message import MessagePart, MessageSet


def test_message_set_init_with_string():
    msg_set = MessageSet(msg_ids="1,2,3")
    assert msg_set.msg_ids == "1,2,3"


def test_message_set_init_with_list():
    msg_set = MessageSet(msg_ids=[1, 2, 3])
    assert msg_set.msg_ids == "1,2,3"


def test_message_set_empty_raises_value_error():
    with pytest.raises(ValueError, match="Message IDs cannot be empty"):
        MessageSet(msg_ids="")


def test_message_set_invalid_id_raises_value_error():
    with pytest.raises(ValueError, match="Invalid message ID: abc"):
        MessageSet(msg_ids="abc")


def test_message_set_invalid_range_raises_value_error():
    with pytest.raises(ValueError, match="Invalid range in message IDs: 10:5"):
        MessageSet(msg_ids="10:5")


def test_message_set_valid_range():
    msg_set = MessageSet(msg_ids="1:10")
    assert msg_set.msg_ids == "1:10"


def test_message_set_mixed_valid_ids():
    msg_set = MessageSet(msg_ids="1,3:5,7")
    assert msg_set.msg_ids == "1,3:5,7"

def test_message_set_valid_star_range():
    msg_set = MessageSet(msg_ids="1:*")
    assert msg_set.msg_ids == "1:*"

def test_message_set_invalid_type_raises_type_error():
    with pytest.raises(TypeError, match="msg_ids should be a string"):
        MessageSet(msg_ids=123)


def test_message_parts_enum():
    assert MessagePart.RFC822 == "RFC822"
    assert MessagePart.BODY == "BODY"
    assert MessagePart.BODY_TEXT == "BODY[TEXT]"
    assert MessagePart.BODY_HEADER == "BODY[HEADER]"
    assert (
        MessagePart.BODY_HEADER_FIELDS == "BODY[HEADER.FIELDS (FROM TO SUBJECT DATE)]"
    )
    assert MessagePart.FLAGS == "FLAGS"
    assert MessagePart.MODSEQ == "MODSEQ"
    assert MessagePart.BODY_STRUCTURE == "BODYSTRUCTURE"
    assert MessagePart.BODY_PEEK == "BODY.PEEK[]"
    assert MessagePart.BODY_PEEK_TEXT == "BODY.PEEK[TEXT]"
    assert MessagePart.BODY_PEEK_HEADER == "BODY.PEEK[HEADER]"
    assert (
        MessagePart.BODY_PEEK_HEADER_FIELDS
        == "BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)]"
    )
    assert MessagePart.BODY_PEEK_ATTACHMENT == "BODY.PEEK[2]"
