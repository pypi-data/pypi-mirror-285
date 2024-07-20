from __future__ import annotations

tablename = 'resources'
create_table = f"""
CREATE TABLE IF NOT EXISTS {tablename} (
    name VARCHAR(256),
    tag VARCHAR(256)
)
"""

indices = {
    'name_index': 'resources(name)',
    'tag_index': 'resources(tag)',
    'name_and_tag_index': 'resources(name, tag)',
}


class Resources:
    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def initialize(cls, conn):
        conn.execute(create_table)

        for indexname, target in indices.items():
            statement = f'CREATE INDEX IF NOT EXISTS {indexname} ON {target}'
            conn.execute(statement)

        return cls(conn)

    def select_all(self):
        query = f'SELECT * FROM {tablename}'
        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def add_tags(self, data: list[tuple[str, str]]) -> None:
        for name, tag in data:
            self.add_tag(name, tag)

    def has_tag(self, name, tag) -> bool:
        query = f'SELECT * FROM {tablename} WHERE name = (?) AND tag = (?)'
        results = self.conn.execute(query, (name, tag)).fetchall()
        return bool(results)

    def add_tag(self, name: str, tag: str) -> None:
        """Add name with tag.

        If name and tag were already added, do nothing.

        Return whether something changed or not."""
        import re

        valid_tag = re.compile(r'[-\w]*$')
        if not valid_tag.match(tag):
            # Let's not have whitespace and other funnies for now.
            raise ValueError(
                'Invalid tag {tag!r}.  '
                'Tags should be consist of alphanumeric characters, -, or _.'
            )

        if self.has_tag(name, tag):
            return

        query = f'INSERT INTO {tablename} VALUES (?, ?)'
        self.conn.execute(query, (name, tag))

    def select_tag(self, tag: str) -> list[str]:
        query = f'SELECT name FROM {tablename} WHERE tag == (?)'
        results = self.conn.execute(query, (tag,)).fetchall()
        return [results[0] for result in results]

    def get_tags(self, name: str) -> set[str]:
        query = f'SELECT tag FROM {tablename} WHERE name == (?)'
        results = self.conn.execute(query, (name,)).fetchall()
        return set(result[0] for result in results)

    def remove(self, name: str) -> None:
        query = f'DELETE FROM {tablename} WHERE name == (?)'
        self.conn.execute(query, (name,))

    def untag(self, name: str, tag: str) -> None:
        query = f'DELETE FROM {tablename} WHERE name == (?) AND tag == (?)'
        self.conn.execute(query, (name, tag))
