from .util import PathResolvable, Snapshot
from aridity import NoSuchPathException
from aridity.config import ConfigCtrl
from aridity.model import Function, Text
from aridity.scope import slashfunction
from lagoon import git
from lagoon.program import ONELINE
import re, subprocess, yaml

singledigit = re.compile('[0-9]')
zeroormorespaces = re.compile(' *')
linefeed = '\n'
toplevelres = PathResolvable('toplevel')

def blockliteral(scope, textresolvable):
    contextindent = scope.resolved('indent').cat()
    text = yaml.dump(textresolvable.resolve(scope).cat(), default_style = '|')
    header, *lines = text.splitlines() # For template interpolation convenience we discard the (insignificant) trailing newline.
    if not lines:
        return Text(header)
    if '...' == lines[-1]:
        lines.pop() # XXX: Could this result in no remaining lines?
    indentunit = scope.resolved('indentunit').cat()
    m = singledigit.search(header)
    if m is None:
        pyyamlindent = len(zeroormorespaces.match(lines[0]).group())
    else:
        pyyamlindent = int(m.group())
        header = f"{header[:m.start()]}{len(zeroormorespaces.fullmatch(indentunit).group())}{header[m.end():]}"
    return Text(f"""{header}\n{linefeed.join(f"{contextindent}{indentunit}{line[pyyamlindent:]}" for line in lines)}""")

def rootpath(scope, *resolvables):
    return slashfunction(scope, toplevelres, *resolvables)

def _toplevel(anydir):
    try:
        return Text(git.rev_parse.__show_toplevel[ONELINE](cwd = anydir))
    except subprocess.CalledProcessError:
        raise NoSuchPathException('Git property: toplevel')

def createparent(soakroot):
    parent = ConfigCtrl().node
    s = (-parent).scope()
    s['|',] = Function(blockliteral)
    s['//',] = Function(rootpath)
    s['toplevel',] = Snapshot(lambda: _toplevel(soakroot))
    (-parent).execute('data = $processtemplate$(from)') # XXX: Too easy to accidentally override?
    parent.indentunit = 4 * ' '
    return parent
