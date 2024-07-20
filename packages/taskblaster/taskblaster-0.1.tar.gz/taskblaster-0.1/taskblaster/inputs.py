class MissingInput(Exception):
    pass


class SerializedInputTable:
    table = 'inputs'

    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def creation_statement(cls) -> str:
        return """\
CREATE TABLE IF NOT EXISTS inputs (
  name VARCHAR(256) PRIMARY KEY,
  input VARCHAR(1024)
)
"""

    @classmethod
    def indices(cls):
        return {'name_index': 'inputs(name)'}

    @classmethod
    def initialize(cls, conn):
        conn.execute(cls.creation_statement())
        for indexname, indexspec in cls.indices().items():
            conn.execute(
                f'CREATE INDEX IF NOT EXISTS {indexname} ON {indexspec}'
            )

    def names(self):
        return [
            obj[0]
            for obj in self.conn.execute('SELECT name FROM inputs').fetchall()
        ]

    def get(self, name: str) -> str:
        query = 'SELECT input FROM inputs WHERE name=(?)'
        serialized_input = self.conn.execute(query, (name,)).fetchone()

        if serialized_input is None:
            raise MissingInput(
                'No serialized inputs in registry.  Maybe this repository '
                'needs to be updated to fix this problem.  '
                'Consider running "tb registry patch-serialized-inputs" to '
                'fix this problem.'
            )
        return serialized_input[0]

    def add(self, name: str, serialized_input: str) -> None:
        assert isinstance(serialized_input, str)
        query = 'INSERT INTO inputs VALUES (?, ?)'
        self.conn.execute(query, (name, serialized_input))

    def remove(self, name: str) -> None:
        query = 'DELETE FROM inputs WHERE name=(?)'
        self.conn.execute(query, (name,))
