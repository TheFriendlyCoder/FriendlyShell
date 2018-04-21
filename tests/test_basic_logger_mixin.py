import logging
from friendlyshell.basic_logger_mixin import BasicLoggerMixin
import pytest


def test_info(caplog):
    caplog.set_level(logging.INFO)

    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text"
    obj.info(expected_text)

    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.INFO == rec.levelno
    assert expected_text == rec.message


def test_info_args(caplog):
    caplog.set_level(logging.INFO)
    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text: Kevin"
    obj.info("Here's my sample text: %s", "Kevin")
    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.INFO == rec.levelno
    assert expected_text == rec.message


def test_info_exception(caplog):
    caplog.set_level(logging.INFO)
    obj = BasicLoggerMixin()
    expected_text1 = "Here's my sample text"
    expected_text2 = "Some Error Here"
    try:
        raise Exception(expected_text2)
    except:
        obj.info(expected_text1, exc_info=True)

    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.INFO == rec.levelno
    assert expected_text1 in rec.message
    assert expected_text2 in caplog.text


def test_warning(caplog):
    caplog.set_level(logging.INFO)

    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text"
    obj.warning(expected_text)

    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.WARNING == rec.levelno
    assert expected_text == rec.message


def test_warning_args(caplog):
    caplog.set_level(logging.INFO)
    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text: Kevin"
    obj.warning("Here's my sample text: %s", "Kevin")
    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.WARNING == rec.levelno
    assert expected_text == rec.message


def test_warning_exception(caplog):
    caplog.set_level(logging.INFO)
    obj = BasicLoggerMixin()
    expected_text1 = "Here's my sample text"
    expected_text2 = "Some Error Here"
    try:
        raise Exception(expected_text2)
    except:
        obj.warning(expected_text1, exc_info=True)

    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.WARNING == rec.levelno
    assert expected_text1 in rec.message
    assert expected_text2 in caplog.text


def test_error(caplog):
    caplog.set_level(logging.INFO)

    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text"
    obj.error(expected_text)

    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.ERROR == rec.levelno
    assert expected_text == rec.message


def test_error_args(caplog):
    caplog.set_level(logging.INFO)
    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text: Kevin"
    obj.error("Here's my sample text: %s", "Kevin")
    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.ERROR == rec.levelno
    assert expected_text == rec.message


def test_error_exception(caplog):
    caplog.set_level(logging.INFO)
    obj = BasicLoggerMixin()
    expected_text1 = "Here's my sample text"
    expected_text2 = "Some Error Here"
    try:
        raise Exception(expected_text2)
    except:
        obj.error(expected_text1, exc_info=True)

    assert 1 == len(caplog.get_records("call"))
    rec = caplog.get_records("call")[0]
    assert logging.ERROR == rec.levelno
    assert expected_text1 in rec.message
    assert expected_text2 in caplog.text


def test_debug(caplog):
    caplog.set_level(logging.DEBUG)

    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text"
    obj.debug(expected_text)

    assert expected_text in caplog.text
    for rec in caplog.get_records("call"):
        if expected_text == rec.message:
            assert rec.levelno == logging.DEBUG


def test_debug_args(caplog):
    caplog.set_level(logging.DEBUG)

    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text: Kevin"
    obj.debug("Here's my sample text: %s", "Kevin")

    assert expected_text in caplog.text
    for rec in caplog.get_records("call"):
        if expected_text == rec.message:
            assert rec.levelno == logging.DEBUG


def test_debug_exception(caplog):
    caplog.set_level(logging.DEBUG)

    obj = BasicLoggerMixin()
    expected_text1 = "Here's my sample text"
    expected_text2 = "Some Error Here"
    try:
        raise Exception(expected_text2)
    except:
        obj.debug(expected_text1, exc_info=True)

    assert expected_text1 in caplog.text
    assert expected_text2 in caplog.text
    for rec in caplog.get_records("call"):
        if expected_text1 == rec.message:
            assert rec.levelno == logging.DEBUG
        if expected_text2 == rec.message:
            assert rec.levelno == logging.DEBUG


def test_no_debug(caplog):
    caplog.set_level(logging.INFO)
    obj = BasicLoggerMixin()
    expected_text = "Here's my sample text"

    obj.debug(expected_text)

    assert expected_text not in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])