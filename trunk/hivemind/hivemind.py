#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from google.appengine.ext import db
from hmdb import Planet
from hmdb import Player
from hmdb import Fleet


class Updater:
    def __init__(self, raw_data=None):
        self.raw_data_list = raw_data.split('&')[1:]

    def update(self):
        first_planet = True
        first_fleet = True
        for info in self.raw_data_list:
            value = info.split('=')[1]
# Planet
            if info.startswith('planet'):
                qf = Fleet.gql('WHERE location_name = :1', value.lower())
                qp = Planet.gql('WHERE name = :1', value)
                db.delete(qf.fetch(999))
                db.delete(qp.fetch(999))
                if not first_planet:
                    planet.put()
                planet = Planet(key_name='_'.join(['planet', value]),
                                name=value)
                first_planet = False
# Stasis
            elif info.startswith('stasis'):
                if value == '0':
                    planet.stasis = False
                else:
                    planet.stasis = True
# Fleet ID
            elif info.startswith('fleetid'):
                if not first_fleet:
                    fleet.put()
                fleet = Fleet(key_name='_'.join(['fleet', value]),
                              location=planet,
                              location_name=planet.name.lower())
                first_fleet = False
# Fleet race
            elif info.startswith('frace'):
                if value == '2':
                    fleet.race = 'xillor'
                elif value == '1':
                    fleet.race = 'azterk'
                else:
                    fleet.race = 'human'
# Fleet owner
            elif info.startswith('owner'):
                player = Player(key_name='_'.join(['player', value]),
                                name=value)
                player.put()
                fleet.owner = player
                fleet.owner_name = value.lower()
# Defend
            elif info.startswith('defend'):
                if value == '0':
                    fleet.defend = False
                else:
                    fleet.defend = True
# Camouflage
            elif info.startswith('camouf'):
                if value == '0':
                    fleet.camo = False
                else:
                    fleet.camouf = True
# Mass bombing
            elif info.startswith('bombing'):
                if value == '0':
                    fleet.bombing = False
                else:
                    fleet.bombing = True
# Scouts
            elif info.startswith('scou'):
                fleet.scouts = value
# Cruisers
            elif info.startswith('crui'):
                fleet.cruisers = value
# Bombers
            elif info.startswith('bomb'):
                fleet.bombers = value
# Destroyers
            elif info.startswith('dest'):
                fleet.destroyers = value
# Carried armies
            elif info.startswith('carmies'):
                fleet.carmies = value
# Ground armies
            elif info.startswith('garmies'):
                fleet.garmies = value
        planet.put()
        fleet.put()


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())
