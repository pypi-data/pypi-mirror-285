from dataclasses import dataclass
from argparse import ArgumentParser
import os
from getpass import getpass

from labcrawler.command import LabCrawlerCommand
from labcrawler.gitlab.query import GitLabQuery

DATATYPES = GitLabQuery.family_attrs('name')


class ListCommand(LabCrawlerCommand):

    datatype: str = ''
    path: str = ''
    name = 'list'
    output = 'text'

    @classmethod
    def add_args(self, parser: ArgumentParser):
        parser.add_argument('datatype', choices=DATATYPES)
        parser.add_argument('--output', '-o', choices=['text', 'yaml'],
                            default='text')
        parser.add_argument('path', default='')

    @LabCrawlerCommand.wrap
    def execute(self):
        host = self.app.config.get('gitlab-host') or 'gitlab.com'
        token = self.app.config.get('gitlab-token')
        if not token:
            token = getpass(f"GitLab Private Token for {host}: ").strip()
        if len(token) != 26:
            raise RuntimeError(
                "GitLab Access Token must contain 26 characters")
        assert self.datatype in DATATYPES
        cls = GitLabQuery.family_member('name', self.datatype)
        query = cls(host, token)
        result = query.run(self.path)
        self.status = f"{len(result)} {self.datatype} listed"
        if self.output == 'text':
            return "\n".join(cls.format(i) for i in result)
        elif self.output == 'yaml':
            return cls.to_yaml(result)
