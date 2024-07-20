import shlex
import shutil
from pathlib import Path
from subprocess import check_output

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives

from taskblaster.util import workdir

tmpdir = None

dct = {
    '': '',
    '\033[0;30m': 'ansi-black',
    '\033[0;31m': 'ansi-red',
    '\033[94m': 'ansi-lightBlue',
    '\033[91m': 'ansi-lightRed',
    '\033[95m': 'ansi-lightPurple',
    '\033[96m': 'ansi-lightCyan',
    '\033[33m': 'ansi-yellow',
    '\033[32m': 'ansi-green',
    '\033[0m': '',
    '\033[0;34m': 'ansi-blue',
    '\x1b[93m': 'ansi-yellow',
}


class TBFile(rst.Directive):
    has_content = True

    node_class = nodes.literal_block

    def run(self):
        folder = self.content[0]
        env = self.state.document.settings.env
        rel_path, path = env.relfn2path(folder)

        shutil.copy(path, tmpdir / Path(path).name)
        return []


class TBInit(rst.Directive):
    has_content = True

    node_class = nodes.literal_block

    def run(self):
        folder = self.content[0]
        assert not Path(folder).is_absolute()
        pth = Path('/tmp/taskblaster') / str(folder) / 'tmprepo'
        from shutil import rmtree

        rmtree(pth, ignore_errors=True)
        pth.mkdir(parents=True)

        global tmpdir
        tmpdir = pth

        return []


class Tokenizer:
    def __init__(self, txt):
        self.txt = txt
        self.index = 0

    def __iter__(self):
        def next_char():
            if self.index == len(self.txt):
                raise StopIteration
            c = self.txt[self.index]
            self.index += 1
            return c

        color_label = ''
        text = ''
        try:
            while True:
                c = next_char()
                if c == '\033':
                    if text != '':
                        yield text, color_label
                        text = ''
                    ansistr = '' + c
                    while c != 'm':
                        c = next_char()
                        ansistr += c
                    color_label = ansistr
                    continue
                text += c
        except StopIteration:
            if text != '':
                yield text, color_label


class TBShellCommand(rst.Directive):
    has_content = True

    node_class = nodes.literal_block

    def run(self):
        command = self.content[0]
        arguments = shlex.split(command)
        global tmpdir
        with workdir(tmpdir):
            output = check_output(arguments, encoding='utf-8')
        txt = f'$ {command}\n'

        children = []
        for text, color in Tokenizer(
            output.replace(str(tmpdir.parent), '/home/myuser')
        ):
            node = nodes.inline('', text)
            node['classes'] = [dct[color]]
            children.append(node)

        node = self.node_class('BLOCKTEXT1', txt, *children)

        return [node]


def setup(app):
    app.add_css_file('ansi.css')
    print('Setting up tb Sphinx Directives (tbinit, tbfile, tbshellcommand)')


directives.register_directive('tbinit', TBInit)
directives.register_directive('tbfile', TBFile)
directives.register_directive('tbshellcommand', TBShellCommand)
