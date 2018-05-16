# -*- coding: utf-8 -*-


class GraphAPIException(Exception):

    def __init__(self, message='', response=None):
        self.message = message
        self.response = response
