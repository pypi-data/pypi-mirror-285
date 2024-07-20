from pathlib import Path
from typing import Any

from taskblaster.hashednode import Node, mkhash


class Entry:
    """Entry in file-based cache.

    Entry wraps a directory and provides access to functionality
    related to how a task is physically stored inside that directory."""

    inputname = 'input.json'
    outputname = 'output.json'

    def __init__(self, directory, json_protocol):
        self.directory = Path(directory)
        self.json_protocol = json_protocol

    def __repr__(self):
        return f'<Entry({self.directory})>'

    @property
    def inputfile(self) -> Path:
        return self.directory / self.inputname

    @property
    def outputfile(self) -> Path:
        return self.directory / self.outputname

    def delete(self):
        assert self.inputfile.parent == self.directory
        assert self.outputfile.parent == self.directory

        self.inputfile.unlink(missing_ok=True)
        self.outputfile.unlink(missing_ok=True)

    def read_inputfile(self):
        buf = self.inputfile.read_bytes()
        digest = mkhash(buf)
        return digest, buf.decode('utf-8')

    def node(self, name) -> Node:
        return Node.fromdata(
            self.json_protocol, self.inputfile.read_text(), name
        )

    def output(self) -> Any:
        # XXX Remove _hook stuff from Entry and remove this method
        output = self.outputfile.read_text()
        return self._hook.loads(output)

    def has_output(self):
        return self.outputfile.exists()

    @property
    def _hook(self):
        return self.json_protocol.outputencoder(self.directory)

    def dump_output(self, output):
        jsontext = self._hook.dumps(output)

        # We first write to out.json.part and then rename to out.json.
        # This means if and when out.json exists, it is guaranteed
        # intact.
        tmpfile = self.outputfile.with_suffix('.part')
        tmpfile.write_text(jsontext)
        tmpfile.rename(self.outputfile)
