from threading import Thread,Condition
import requests


class MutilThreadDownload:
    def __init__(self,url):
        self.url=url
