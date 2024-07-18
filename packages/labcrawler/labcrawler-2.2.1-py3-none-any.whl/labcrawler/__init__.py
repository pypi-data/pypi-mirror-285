from wizlib.app import WizApp
from wizlib.ui_handler import UIHandler
from wizlib.config_handler import ConfigHandler

from labcrawler.command import LabCrawlerCommand


class LabCrawlerApp(WizApp):

    base = LabCrawlerCommand
    name = 'labc'
    handlers = [ConfigHandler, UIHandler]
