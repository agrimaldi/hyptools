#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from google.appengine.ext import db


class Player(db.Model):
    name = db.StringProperty(required=True)

class Planet(db.Model):
    name = db.StringProperty(required=True)
    stasis = db.BooleanProperty(required=True)

class Float(db.Model):
    tech_lvl = db.IntegerProperty(required=True)
    race = db.IntegerProperty(required=True)
    defend = db.BooleanProperty(required=True)
    camouf = db.BooleanProperty(required=True)
    scouts = db.IntegerProperty()
    destroyers = db.IntegerProperty()
    bombers = db.IntegerProperty()
    cruisers = db.IntegerProperty()
    owner = db.ReferenceProperty(Player)
    location = db.ReferenceProperty(Planet)

def main():
    player1 = Player(key_name="player_sopo", name="sopo")
    player2 = Player(key_name="player_azerty", name="azerty")
    player3 = Player(key_name="player_qsdf", name="qsdf")
    player1.put()
    player2.put()
    player3.put()

    planet1 = Planet(key_name="planet_sdf", name="sdf", stasis=False)
    planet2 = Planet(key_name="planet_dsq", name="dsq", stasis=True)
    planet1.put()
    planet2.put()

    float1 = Float(key_name="float_876", tech_lvl=43, race=2, defend=False, camouf=False, owner=player1, location=planet1)
    float2 = Float(key_name="float_394", tech_lvl=32, race=2, defend=False, camouf=False, owner=player3, location=planet2)
    float3 = Float(key_name="float_984", tech_lvl=42, race=2, defend=True, camouf=False, owner=player2, location=planet1)
    float4 = Float(key_name="float_3484", tech_lvl=42, race=2, defend=True, camouf=False, owner=player2, location=planet1)
    float5 = Float(key_name="float_39084", tech_lvl=42, race=2, defend=True, camouf=False, owner=player2, location=planet1)
    float6 = Float(key_name="float_3944", tech_lvl=43, race=2, defend=False, camouf=False, owner=player1, location=planet1)
    float7 = Float(key_name="float_3924", tech_lvl=43, race=2, defend=False, camouf=False, owner=player1, location=planet1)
    float8 = Float(key_name="float_34", tech_lvl=43, race=2, defend=False, camouf=False, owner=player1, location=planet1)
    float1.put()
    float2.put()
    float3.put()
    float4.put()
    float5.put()
    float6.put()
    float7.put()
    float8.put()

    query1 = Float.all()
    results = query1.fetch(10)
    for result in results:
        if result.owner.name == "sopo":
            print(result.location.name, result.location.stasis, result.owner.name)



if __name__ == '__main__':
    sys.exit(main())
