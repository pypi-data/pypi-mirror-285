from datapools.worker.plugins.base_plugin import BasePlugin, BaseTag
from datapools.worker.plugins.ftp import FTPPlugin
from datapools.worker.types import WorkerContext

from .fixtures import *


def test_tag_parsing():

    t = BasePlugin.parse_tag_in_str("\n https://openlicense.ai/asd")
    assert isinstance(t, BaseTag)
    assert str(t) == "asd"
    assert t.is_keepout() is False

    t = BasePlugin.parse_tag_in_str("https://openlicense.ai/t/asd\nblabla")
    assert isinstance(t, BaseTag)
    assert str(t) == "asd"
    assert t.is_keepout() is False

    t = BasePlugin.parse_tag_in_str("blabla openlicense.ai/t/asd \n")
    assert isinstance(t, BaseTag)
    assert str(t) == "asd"
    assert t.is_keepout() is False

    t = BasePlugin.parse_tag_in_str("xopenlicense.ai/t/asd")
    assert t is None

    t = BasePlugin.parse_tag_in_str("\nhttps://openlicense.ai/n/asd blabla")
    assert isinstance(t, BaseTag)
    assert str(t) == "asd"
    assert t.is_keepout() is True

    t = BasePlugin.parse_tag_in_str("openlicense.ai/n/asd blabla")
    assert isinstance(t, BaseTag)
    assert str(t) == "asd"
    assert t.is_keepout() is True

    t = BasePlugin.parse_tag_in_str("xopenlicense.ai/n/asd")
    assert t is None

    t = BasePlugin.parse_tag_in_str("https://openlicense.ai/x/asd")
    assert t is None

    t = BasePlugin.parse_tag_in_str("openlicense.ai/x/asd")
    assert t is None


def test_ftp_link_parsing():
    (user, passwd, host, port) = FTPPlugin.parse_ftp_url("ftp://user:password@host:21")
    assert user == "user"
    assert passwd == "password"
    assert host == "host"
    assert port == 21

    (user, passwd, host, port) = FTPPlugin.parse_ftp_url("ftp://host:21")
    assert user == "anonymous"
    assert passwd == ""
    assert host == "host"
    assert port == 21

    (user, passwd, host, port) = FTPPlugin.parse_ftp_url("ftp://user@host:22")
    assert user == "user"
    assert passwd == ""
    assert host == "host"
    assert port == 22

    (user, passwd, host, port) = FTPPlugin.parse_ftp_url("ftp://user@host")
    assert user == "user"
    assert passwd == ""
    assert host == "host"
    assert port == 21

    (user, passwd, host, port) = FTPPlugin.parse_ftp_url("ftp://host")
    assert user == "anonymous"
    assert passwd == ""
    assert host == "host"
    assert port == 21


def test_busy_count(session):
    class A(BasePlugin):
        @staticmethod
        def is_supported(url):
            return True

        async def process(self, task):
            pass

    class B(BasePlugin):
        @staticmethod
        def is_supported(url):
            return True

        async def process(self, task):
            pass

    ctx = WorkerContext(session=session)

    assert A.get_busy_count() == 0
    assert B.get_busy_count() == 0
    a = A(ctx)
    a.is_busy = True
    assert A.get_busy_count() == 1
    assert B.get_busy_count() == 0
    b = B(ctx)
    b.is_busy = True
    assert A.get_busy_count() == 1
    assert B.get_busy_count() == 1
    a.is_busy = False
    assert A.get_busy_count() == 0
    assert B.get_busy_count() == 1
    b.is_busy = False
    assert A.get_busy_count() == 0
    assert B.get_busy_count() == 0


def test_domains():
    assert BasePlugin.is_same_or_subdomain("bbc.m.wikipedia.org", "www.wikipedia.org") is True
    assert BasePlugin.is_same_or_subdomain("pl.m.wikipedia.org", "pl.wikipedia.org") is False
