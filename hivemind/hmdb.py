#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db


class Planet(db.Model):
    """Planet model.
    Contains information about a planet :
        - The name of the planet
        - Whether stasis is up or down
        - The date at which the planet was last modified
    """
    name = db.StringProperty(required=True)
    stasis = db.StringProperty()
    date = db.DateTimeProperty()

    @property
    def lfleets(self):
        lfleets = []
        for fleet in  self.fleets:
            lfleets.append(fleet)
        return lfleets


class Player(db.Model):
    """Player model.
    Contains information about a player :
        - The name of the player
    """
    name = db.StringProperty(required=True)


class Fleet(db.Model):
    """Fleet model.
    Contains information about a fleet.
        - The race
        - The mode (defending or attacking)
        - Whether it is camouflaged or not
        - Whether mass bombing is enabled
        - It's composition (scouts, destroyers, cruisers, bombers, armies)
        - The owner of the fleet
        - The planet it is on
    """
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

    def set_bombing(self, status):
        self.bombing = status

    def set_scou(self, value):
        self.scou = (value == '0' and '-' or value)

    def set_crui(self, value):
        self.crui = (value == '0' and '-' or value)

    def set_bomb(self, value):
        self.bomb = (value == '0' and '-' or value)

    def set_dest(self, value):
        self.dest = (value == '0' and '-' or value)

    def set_carmies(self, value):
        self.carmies = (value == '0' and '-' or value)

    def set_garmies(self, value):
        self.garmies = (value == '0' and '-' or value)

    def set_frace(self, value):
        if value == '0':
            self.frace = 'Human'
        elif value == '1':
            self.frace = 'Azterk'
        else:
            self.frace = 'Xillor'
