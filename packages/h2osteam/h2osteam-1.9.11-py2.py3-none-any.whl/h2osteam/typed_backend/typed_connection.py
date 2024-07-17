# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


import requests

from h2osteam.backend import SteamConnection

from h2osteam.typed_backend.typed_api import TypedSteamApi



class TypedSteamConnection(TypedSteamApi):
    def __init__(self, steam: SteamConnection=None):
        self.steam = steam


    def call(self, method, params):
        return self.steam.call(method, params)