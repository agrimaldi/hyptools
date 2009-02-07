#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db


class Planet(db.Model):
    name = db.StringProperty(required=True)
    stasis = db.StringProperty()
#    players = db.StringListProperty()


class Player(db.Model):
    name = db.StringProperty(required=True)
#    locations = db.StringListProperty()


class Fleet(db.Model):
    frace = db.StringProperty()
    defend = db.StringProperty()
    camouf = db.StringProperty()
    bombing = db.StringProperty()
    scou = db.StringProperty(default='-')
    dest = db.StringProperty(default='-')
    bomb = db.StringProperty(default='-')
    crui = db.StringProperty(default='-')
    carmies = db.StringProperty(default='-')
    garmies = db.StringProperty(default='-')
    owner_name = db.StringProperty()
    location_name = db.StringProperty()
    owner = db.ReferenceProperty(Player, collection_name='fleets')
    location = db.ReferenceProperty(Planet, collection_name='fleets')

    def set_defend(self, status):
        self.defend = status

    def set_camouf(self, status):
        self.camouf = status

    def set_bombing(self, state):
        self.bombing = state

    def set_scou(self, value):
        self.scou = value

    def set_crui(self, value):
        self.crui = value

    def set_bomb(self, value):
        self.bomb = value

    def set_dest(self, value):
        self.dest = value

    def set_carmies(self, value):
        self.carmies = value

    def set_garmies(self, value):
        self.garmies = value

    def set_frace(self, value):
        self.frace = value
