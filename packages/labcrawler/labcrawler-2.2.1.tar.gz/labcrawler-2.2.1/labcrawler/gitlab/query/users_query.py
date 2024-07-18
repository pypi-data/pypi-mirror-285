from collections import defaultdict
from dataclasses import dataclass

from yaml import dump

from . import GitLabQuery


@dataclass
class GitLabUsersQuery(GitLabQuery):

    name = 'users'

    template = """
        query {{
            users(after: "{cursor}") {{
                nodes {{
                    username
                    state
                    publicEmail
                    name
                    emails(after: "") {{
                        nodes {{
                            email
                        }}
                    }}
                }}
                pageInfo {{
                    endCursor
                    hasNextPage
                }}
            }}
        }}
        """

    @staticmethod
    def to_yaml(values):
        result = {}
        for val in values:
            result[val['username']] = {
                'state': val['state'],
                'public-email': val['publicEmail'],
                'name': val['name'],
                'emails': [n['email'] for n in val['emails']['nodes']]
            }
        yaml = dump(result)
        return yaml

    @staticmethod
    def format(value):
        return value['username']

    @staticmethod
    def parse(node):
        return node

    def run(self, path: str = ''):
        users = []

        def parsefunc(data):
            connection = data['users']
            for node in connection['nodes']:
                if node['state'] == 'active':
                    users.append(self.parse(node))
            return connection
        self.perform_query(parsefunc, path=path)
        return sorted(users, key=lambda g: g['username'])
