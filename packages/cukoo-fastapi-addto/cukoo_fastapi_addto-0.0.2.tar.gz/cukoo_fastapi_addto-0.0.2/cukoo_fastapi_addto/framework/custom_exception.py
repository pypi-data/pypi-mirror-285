# -*- encoding: utf-8 -*-
'''
@File    :   custom_exception.py
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

class ParamError(Exception):
    def __init__(self, message: str="Request Param Error"):
        self.message = message

class TokenError(Exception):
    def __init__(self, message: str="Token Error"):
        self.message = message

class NotFound(Exception):
    def __init__(self, message: str="Not Found"):
        self.message = message