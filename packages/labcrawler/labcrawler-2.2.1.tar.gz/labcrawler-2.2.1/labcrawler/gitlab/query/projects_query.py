from dataclasses import dataclass

from . import GitLabQuery
from .subgroups_query import GitLabGroupsQuery


@dataclass
class GitLabProjectsQuery(GitLabQuery):

    name = 'projects'

    template = """
        query {{
            group(fullPath: "{path}") {{
                projects(after: "{cursor}") {{
                    nodes {{
                        fullPath
                        ciConfigPathOrDefault
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
            'ciConfigPathOrDefault': node['ciConfigPathOrDefault']
        }

    def run(self, path: str, include_subgroups=True):
        if not path:
            return
        if include_subgroups:
            groupsquery = GitLabGroupsQuery(self.host, self.token)
            subgroups = groupsquery.run(path)
            subgrouppaths = [s['fullPath'] for s in subgroups]
        else:
            subgrouppaths = [path]
        projects = []

        def parsefunc(data):
            connection = data['group']['projects']
            for node in connection['nodes']:
                projects.append(self.parse(node))
            return connection
        for subgrouppath in subgrouppaths:
            self.perform_query(parsefunc, path=subgrouppath)
        return sorted(projects, key=lambda p: p['fullPath'])
