from aridity.model import Resolvable
from threading import Lock

class Snapshot(Resolvable):

    class Result:

        def __init__(self, eornone, obj):
            self.eornone = eornone
            self.obj = obj

        def get(self):
            if self.eornone is not None:
                raise self.eornone
            return self.obj

    def __init__(self, factory):
        self.lock = Lock()
        self.factory = factory

    def _loadresult(self):
        with self.lock:
            try:
                self.result
            except AttributeError:
                f = self.factory
                try:
                    obj = f()
                    eornone = None
                except Exception as e:
                    obj = None
                    eornone = e
                self.result = self.Result(eornone, obj)

    def resolve(self, scope):
        try:
            r = self.result
        except AttributeError:
            self._loadresult()
            r = self.result
        return r.get()

class PathResolvable(Resolvable):

    def __init__(self, *path):
        self.path = path

    def resolve(self, scope):
        return scope.resolved(*self.path)
