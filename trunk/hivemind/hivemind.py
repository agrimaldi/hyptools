#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import datetime
from google.appengine.ext import db
from hmdb import Planet
from hmdb import Player
from hmdb import Fleet


NUM_RGX = re.compile(r'(\d*\.?\d+)(?==)')

class Updater:
    def __init__(self, raw_data=None):
        self.__raw_data_list = NUM_RGX.sub('', raw_data).split('&')[1:]
        self.__date = datetime.datetime.now()
        self.__chunk_list = []
        self.__planet_key_list = []
        self.__tmp_fleet = None
        self.__tmp_planet = None
        self.__keys = {
                'defend': "set_defend",
                'camouf': "set_camouf",
                'bombing': "set_bombing",
                'scou': "set_scou",
                'crui': "set_crui",
                'bomb': "set_bomb",
                'dest': "set_dest",
                'carmies': "set_carmies",
                'garmies': "set_garmies",
                'frace': "set_frace"
            }

    def chop(self, chunk_size):
        """
        Splits the data list in <size> elements long lists
        """
        self.__chunk_list = []
        for i in xrange(0, len(self.__raw_data_list), chunk_size):
            self.__chunk_list.append(self.__raw_data_list[i:i+chunk_size])

    def update(self, chunk):
        """
        Parses the chunk given as first argument, and updates the database
        with the extracted values.
        """
        first_planet = True
        first_fleet = True
        first_player = True
        if self.__tmp_fleet:
            fleet = self.__tmp_fleet
            first_fleet = False
        if self.__tmp_planet:
            qf = Fleet.gql(
                'WHERE location_name = :1',
                self.__tmp_planet.name.lower()
            )
            planet = self.__tmp_planet
            first_planet = False
        for info in chunk:
            key, value = info.split('=')
            if key in self.__keys:
                fleet.__getattribute__(self.__keys[key])(value)
            elif info.startswith('planet'):
                if first_planet:
                    qf = Fleet.gql(
                        'WHERE location_name = :1',
                        value.lower()
                    )
                else:
                    qf.bind(value.lower())
                    planet.put()
                db.delete(qf.fetch(50))
                if value not in self.__planet_key_list:
                    self.__planet_key_list.append(value)
                    planet = Planet(
                        key_name='_'.join(['planet', value.lower()]),
                        name=value,
                        date=self.__date
                    )
                first_planet = False
            elif info.startswith('fleetid'):
                if not first_fleet:
                    fleet.put()
                fleet = Fleet(
                    key_name='_'.join(['fleet', value]),
                    location=planet,
                    location_name=planet.name.lower()
                )
                first_fleet = False
            elif info.startswith('owner'):
                if first_player:
                    qp = Player.gql(
                        "WHERE name = :1",
                        value
                    )
                    first_player = False
                else:
                    qp.bind(value)
                player = qp.get()
                if not player:
                    player = Player(
                        key_name='_'.join(['player', value.lower()]),
                        name=value
                    )
                    player.put()
                fleet.owner = player
                fleet.owner_name = value.lower()
            elif info.startswith('stasis'):
                planet.stasis = value
        planet.put()
        fleet.put()
        self.__tmp_fleet = fleet
        self.__tmp_planet = planet

    def get_chuck_list(self):
        return self.__chunk_list

    chunk_list = property(get_chuck_list)


def main():
    pass

if __name__ == '__main__':
    main()
