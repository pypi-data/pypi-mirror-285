from dataclasses import dataclass
from requests import post
from requests import codes

from wizlib.class_family import ClassFamily


@dataclass
class GitLabQuery(ClassFamily):
    """ A GraphQL query"""

    host: str = None
    token: str = None

    @staticmethod
    def format(value):
        return value['fullPath']

    @property
    def url(self):
        return f"https://{self.host}/api/graphql"

    @property
    def headers(self):
        return {
            'Private-Token': self.token,
            'Content-Type': 'application/json'
        }

    def perform_query(self, parsefunc, **kwargs):
        """
        Run the query and handles pagination. Assumes there is only one
        connection returning an endCursor. Does not return a value.

        Arguments:

        parsefunc - A function that takes the JSON data node, collects the
        information it needs, and returns only the path to the connection that
        will be used for pagination. Use a closure in the subclass to collect
        your results.

        **kwargs - Passed to self.template for substitution.

        """

        hasNextPage = True
        endCursor = ""
        while hasNextPage:
            query = self.template.format(cursor=endCursor, **kwargs)
            response = post(self.url, headers=self.headers,
                            json={'query': query})
            if response.status_code == codes.ok:
                connection = parsefunc(response.json()['data'])
                # collection.extend(connection['nodes'])
                hasNextPage = connection['pageInfo']['hasNextPage']
                if hasNextPage:
                    endCursor = connection['pageInfo']['endCursor']
            else:
                try:
                    message = response.json()['message']
                except Exception:
                    message = f"Error {response.status_code} from {self.url}"
                raise Exception(message)
