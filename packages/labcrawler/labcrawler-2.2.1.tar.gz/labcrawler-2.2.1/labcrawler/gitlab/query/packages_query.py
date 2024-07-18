from collections import defaultdict
from dataclasses import dataclass
from yaml import dump

from . import GitLabQuery
from .subgroups_query import GitLabGroupsQuery


@dataclass
class GitLabPackagesQuery(GitLabQuery):
    """Hard-coded to only pull NPM packages at this point"""

    name = 'packages'

    @staticmethod
    def format(value):
        return f"{value['name']:<60}{value['version']}"

    @staticmethod
    def to_yaml(values):
        indexed = defaultdict(list)
        for val in values:
            indexed[val['name']].append(val['version'])
        yaml = dump(dict(indexed))
        return yaml

    template = """
        query {{
            project(fullPath: "{path}") {{
                packages({type_expr} after: "{cursor}") {{
                    nodes {{
                        name
                        packageType
                        version
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }}
            }}
        }}
    """

    @staticmethod
    def parse(node):
        return {
            'name': node['name'],
            'packageType': node['packageType'],
            'version': node['version']
        }

    def run(self, path: str):
        if not path:
            return

        packages = []

        def parsefunc(data):
            connection = data['project']['packages']
            for node in connection['nodes']:
                packages.append(self.parse(node))
            return connection

        type_expr = 'packageType: NPM, '
        self.perform_query(parsefunc, path=path, type_expr=type_expr)
        return sorted(packages, key=lambda g: (g['name'], g['version']))
