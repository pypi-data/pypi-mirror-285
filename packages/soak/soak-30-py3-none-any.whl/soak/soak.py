'Process aridity templates as per all soak.arid configs in directory tree.'
from . import cpuexecutor
from .context import createparent
from .multifork import Tasks
from .terminal import getterminal, Style
from argparse import ArgumentParser
from diapyr.util import invokeall
from functools import partial
from lagoon import diff
from lagoon.util import atomic
from pathlib import Path
import logging, os, sys

log = logging.getLogger(__name__)

class SoakConfig:

    soakkey = 'soak'

    def __init__(self, parent, configpath):
        self.node = (-parent).childctrl().node
        self.node.cwd = str(configpath.parent.resolve())
        (-self.node).printf(". %s", configpath.name)
        self.reltargets = [Path(rt) for rt, _ in (-getattr(self.node, self.soakkey)).scope().resolvables.items()]
        self.dirpath = configpath.parent

    def process(self, reltarget):
        with atomic(self.dirpath / reltarget) as partpath:
            (-self.node).scope().resolved(self.soakkey, str(reltarget), 'data').writeout(partpath)

    def origtext(self, reltarget):
        return getattr(getattr(self.node, self.soakkey), str(reltarget)).diff

    def diff(self, origtext, reltarget):
        diff._us[print]('--color=always', '-', self.dirpath / reltarget, input = origtext, check = False)

def main():
    logging.basicConfig(format = "[%(levelname)s] %(message)s", level = logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument('-n', action = 'store_true')
    parser.add_argument('-d', action = 'store_true')
    parser.add_argument('-v', action = 'store_true', help = 'show debug logging')
    config = parser.parse_args()
    if not config.v:
        logging.getLogger().setLevel(logging.INFO)
    soakroot = Path('.')
    parent = createparent(soakroot)
    soakconfigs = [SoakConfig(parent, p) for p in soakroot.rglob('soak.arid')]
    if not config.n:
        terminal = getterminal()
        tasks = Tasks()
        for soakconfig in soakconfigs:
            for reltarget in soakconfig.reltargets:
                task = partial(soakconfig.process, reltarget)
                task.index = len(tasks)
                task.target = soakconfig.dirpath / reltarget
                terminal.head(task.index, task.target, Style.pending)
                tasks.append(task)
        tasks.started = lambda task: terminal.head(task.index, task.target, Style.running)
        tasks.stdout = lambda task, line: terminal.log(task.index, sys.stdout, line)
        tasks.stderr = lambda task, line: terminal.log(task.index, sys.stderr, line)
        tasks.stopped = lambda task, code: terminal.head(task.index, task.target, Style.abrupt if code else Style.normal)
        tasks.drain(os.cpu_count())
    if config.d:
        with cpuexecutor() as executor:
            diffs = []
            for soakconfig in soakconfigs:
                for reltarget in soakconfig.reltargets:
                    diffs.append(partial(lambda soakconfig, origtextfuture, reltarget: soakconfig.diff(origtextfuture.result(), reltarget),
                            soakconfig, executor.submit(soakconfig.origtext, reltarget), reltarget))
            invokeall(diffs)

if '__main__' == __name__:
    main()
