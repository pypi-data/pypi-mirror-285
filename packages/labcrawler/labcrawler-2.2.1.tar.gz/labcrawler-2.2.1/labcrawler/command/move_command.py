from dataclasses import dataclass
from argparse import ArgumentParser
import os
from getpass import getpass
import logging

# Query-specific imports
from urllib.parse import quote
from requests import put
from requests import codes

from labcrawler.command import LabCrawlerCommand
from labcrawler.gitlab.query import GitLabQuery


class MoveCommand(LabCrawlerCommand):
    """ Requires owner permission on the project """

    datatype: str = ''
    namespace: str = ''
    name = 'move'

    @classmethod
    def add_args(self, parser: ArgumentParser):
        parser.add_argument('datatype', choices=['projects'])
        parser.add_argument('namespace')

    @LabCrawlerCommand.wrap
    def execute(self):

        # TODO: Move the query to a shared query class

        host = self.app.config.get('gitlab-host') or 'gitlab.com'
        token = self.app.config.get('gitlab-token')
        if not host:
            raise RuntimeError("Missing host for GitLab API call")
        elif not token:
            # This is going to break with using input?
            token = getpass(f"GitLab Private Token for {host}: ").strip()
        if len(token) != 26:
            raise RuntimeError(
                "GitLab Access Token must contain 26 characters")

        params = {'namespace': quote(self.namespace)}
        headers = {
            'Private-Token': token,
            'Content-Type': 'application/json'
        }

        result = ""
        repo_paths = [s for p in self.input.splitlines() if (s := p.strip())]
        for repo_path in repo_paths:

            path = quote(repo_path, safe='')
            url = f"https://{host}/api/v4/projects/{path}/transfer"
            response = put(url, params=params, headers=headers)
            logging.info(f"{url} - {str(params)} - {response.status_code}")

            if response.status_code == codes.ok:
                result += response.json()['path_with_namespace']
            else:
                try:
                    message = response.json()['message']
                except Exception:
                    message = f"Error {response.status_code} from {url}"
                raise Exception(message)

        self.status = f"Moved {len(result.splitlines())} " + \
            f"projects to {self.namespace}"
        return result
