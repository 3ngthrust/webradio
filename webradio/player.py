from .base import ignore
from . import pool
from . import single


class Player(object):
    def __init__(self, *, basepath, urls, prebuffering=False):
        self.client = None
        self.server = None

        self.basepath = basepath
        self._urls = urls

        self.prebuffering = prebuffering

    def _initialize_prebuffered(self):
        n_urls = len(self._urls)
        self.server = pool.Server(
            basepath=self.basepath,
            num=n_urls,
            )

        self.client = pool.Client(self.server)
        self.client.urls = self._urls

    def _initialize_single(self):
        self.server = single.Server(basepath=self.basepath)
        self.client = single.Client(self.server)
        self.client.urls = self._urls

    def shutdown(self):
        self.client.disconnect()
        self.server.shutdown()

    @property
    def prebuffering(self):
        return self._prebuffering

    @prebuffering.setter
    def prebuffering(self, new_state):
        if self.server is not None and self.prebuffering == new_state:
            return

        with ignore(AttributeError):
            self.shutdown()

        if new_state:
            self._initialize_prebuffered()
        else:
            self._initialize_single()

        self._prebuffering = new_state

    def __getattr__(self, name):
        # forward everything that is not defined here to the current client
        return getattr(self.client, name)

    def __setattr__(self, name, value):
        # FIXME: this is really hacky
        # if there is another way which does not involve hardcoding anything
        # and which does hopefully not involve metaclasses, that should
        # be used instead
        # Oh, one way to do it would be to explicitly use super().__setattr__,
        # but that looks somewhat ugly
        names = [
            "basepath",
            "urls",
            "client",
            "server",
            "_urls",
            "prebuffering",
            "_prebuffering",
            ]
        if name in names:
            super().__setattr__(name, value)
        else:
            setattr(self.client, name, value)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.shutdown()
