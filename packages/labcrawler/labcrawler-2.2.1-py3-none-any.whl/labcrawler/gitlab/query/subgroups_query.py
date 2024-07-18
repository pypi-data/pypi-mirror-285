from dataclasses import dataclass

from . import GitLabQuery


@dataclass
class GitLabGroupsQuery(GitLabQuery):

    name = 'subgroups'

    template = """
        query {{
            group(fullPath: "{path}") {{
                fullPath
                projects {{
                    count
                }}
                descendantGroups(after: "{cursor}") {{
                    nodes {{
                        fullPath
                        projects {{
                            count
                        }}
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
            'fullPath': node['fullPath'],
            'projects_count': node['projects']['count']
        }

    def run(self, path: str):
        if not path:
            return
        groups = []

        def parsefunc(data):
            root = data['group']
            if not groups:
                groups.append(self.parse(root))
            connection = root['descendantGroups']
            for node in connection['nodes']:
                groups.append(self.parse(node))
            return connection
        self.perform_query(parsefunc, path=path)
        return sorted(groups, key=lambda g: g['fullPath'])
