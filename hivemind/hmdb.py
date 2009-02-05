#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db


class Planet(db.Model):
    name = db.StringProperty(required=True)
    stasis = db.StringProperty()


class Player(db.Model):
    name = db.StringProperty(required=True)


class Fleet(db.Model):
    race = db.StringProperty()
    defend = db.StringProperty()
    camouf = db.StringProperty()
    bombing = db.StringProperty()
    delay = db.StringProperty(default='-')
    scouts = db.StringProperty(default='-')
    destroyers = db.StringProperty(default='-')
    bombers = db.StringProperty(default='-')
    cruisers = db.StringProperty(default='-')
    carmies = db.StringProperty(default='-')
    garmies = db.StringProperty(default='-')
    owner_name = db.StringProperty()
    location_name = db.StringProperty()
    owner = db.ReferenceProperty(Player)
    location = db.ReferenceProperty(Planet)
