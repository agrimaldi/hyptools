#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import string
import re


PRICE = {
    "Cruisers"      : 48000,
    "Destroyers"    : 8000,
    "Scouts"        : 1200,
    "Bombers"       : 8000
}
POWER = {
    "Cruisers"      : 511,
    "Destroyers"    : 80,
    "Scouts"        : 12,
    "Bombers"       : 34
}
DATE_RGX = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", re.M)
FLEET_RGX = re.compile(
    r"^(\w+ ?\w+)\s+"
    r"([.M\d]+)\s+"
    r"([.M\d]+)\s+"
    r"([.?M\d]+)\s+"
    r"([.M\d]+)\s+"
    r"([.?M\d]+)\s+"
    r"([.M\d]+)$",
    re.M)
REGX = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$)"
    r"\s+"
    r"^Planet\s(?P<name>\b[-\w]+\b)$",
    re.M)
TECH_RGX = re.compile(
    r"([\d]+)%.*"
    r"(defending|attacking) "
    r"(armies|fleets) "
    r"\(([\d.]+)"
    r".*?"
    r"([\d.]+)",
    re.M)


class Analysis(dict):
    """
    Wrapper for the BattleReport class.
    This class is used to analyse several battle reports in a row.
    Battle reports are stored as a dictionary whose keys are the name of the
    planet, and values are the forum friendly reports.
    """
    def __init__(self, raw_data=None):
        self.__parse(raw_data.replace('\r', ''))

    def __parse(self, input_str):
        """
        Parse the data and populates the self dictionary.
        """
        start_indexes = [m.start() for m in DATE_RGX.finditer(input_str)]
        end_indexes = [i-5 for i in start_indexes[1:]] + [None]
        list_report = [BattleReport(input_str[start:end])
                        for start, end in zip(start_indexes, end_indexes)]
        for bt in list_report:
            if bt.name not in self:
                self[bt.name] = [bt]
            else:
                self[bt.name].append(bt)


class BattleReport:
    def __init__(self, raw_battle_report=None):
        self.name = ''
        self.date = ''
        self.atk_ga_lvl = ''
        self.atk_ga_bonus = ''
        self.atk_fleet_lvl = ''
        self.atk_fleet_bonus = ''
        self.atk_lost_cash = ''
        self.atk_init_power = ''
        self.atk_lost_power = ''
        self.atk_perc = 0
        self.atk_report = ''
        self.def_ga_lvl = ''
        self.def_ga_bonus = ''
        self.def_fleet_lvl = ''
        self.def_fleet_bonus = ''
        self.def_lost_cash = ''
        self.def_init_power = ''
        self.def_lost_power = ''
        self.def_perc = 0
        self.def_report = ''
        if raw_battle_report is not None:
            self.__parse(raw_battle_report)

    def __int2round(self, num):
        """
        This method converts an integer to a rounded string.
        """
        if num < 1000:
            return str(num)
        elif num >= 1000 and num < 1000000:
            return str(round(num / 1000.0, 1)) + "k"
        elif num >= 1000000 and num < 1000000000:
            return str(round(num / 1000000.0, 1)) + "m"
        else:
            return str(round(num / 1000000000.0, 1)) + "b"

    def __round2int(self, rnum):
        """
        Converts strings such as "3.8M" to the corresponding integer value
        """
        if rnum.endswith('M', -1):
            return int(float(rnum[:-1]) * 1000000)
        else:
            return int(rnum)

    def __parse(self, data):
        atkInitPow = 0
        atkLostPow = 0
        atkLostPri = 0
        defInitPow = 0
        defLostPow = 0
        defLostPri = 0
        atk_techs = {
            'armies':   {
                'bonus': '0',
                'level': 'N/A'
            },
            "fleets":   {
                'bonus': '0',
                'level': 'N/A'}
        }
        def_techs = {
            'armies':   {
                'bonus': '0',
                'level': 'N/A'
            },
            'fleets':   {
                'bonus': '0',
                'level': 'N/A'}
        }
        atk_units = {}
        def_units = {}
        match = REGX.search(data)
        fleets = FLEET_RGX.findall(data)
        techs = TECH_RGX.findall(data)
        for techdata in techs:
            if techdata[1] == "defending":
                def_techs[techdata[2]] = {
                    'bonus': techdata[0],
                    'level': techdata[3]
                }
                atk_techs[techdata[2]] = {
                    'bonus': '0',
                    'level': techdata[4]
                }
            elif techdata[1] == "attacking":
                atk_techs[techdata[2]] = {
                    'bonus': techdata[0],
                    'level': techdata[3]
                }
                def_techs[techdata[2]] = {
                    'bonus': '0',
                    'level': techdata[4]
                }
        for ship in fleets:
            def_units[ship[0]] = {
                'init': ship[3],
                'lost': ship[4]
            }
            atk_units[ship[0]] = {
                'init': ship[5],
                'lost': ship[6]
            }
        for unit, amount in atk_units.iteritems():
            self.atk_report = ''.join([
                self.atk_report,
                unit,
                amount['init'].rjust(27-len(unit)),
                amount['lost'].rjust(13), '\n'])
            if unit != "Ground Armies" and unit != "Carried Armies":
                atkInitPow += self.__round2int(amount['init']) * POWER[unit]
                atkLostPow += self.__round2int(amount['lost']) * POWER[unit]
                atkLostPri += self.__round2int(amount['lost']) * PRICE[unit]
        for unit, amount in def_units.iteritems():
            self.def_report = ''.join([
                self.def_report,
                unit,
                amount['init'].rjust(27-len(unit)),
                amount['lost'].rjust(13), '\n'])
            if unit != "Ground Armies" and unit != "Carried Armies":
                defInitPow += self.__round2int(amount['init']) * POWER[unit]
                defLostPow += self.__round2int(amount['lost']) * POWER[unit]
                defLostPri += self.__round2int(amount['lost']) * PRICE[unit]
        self.date = match.group('date')
        self.name = match.group('name')
        self.atk_ga_lvl = atk_techs["armies"]["level"]
        self.atk_ga_bonus = atk_techs["armies"]["bonus"]
        self.atk_fleet_lvl = atk_techs["fleets"]["level"]
        self.atk_fleet_bonus = atk_techs["fleets"]["bonus"]
        self.atk_lost_cash = self.__int2round(atkLostPri)
        self.atk_init_power = self.__int2round(atkInitPow)
        self.atk_lost_power = self.__int2round(atkLostPow)
        self.atk_perc = (
            atkInitPow and [int(100.0*atkLostPow/atkInitPow)] or [0])[0]
        self.def_ga_lvl = def_techs["armies"]["level"]
        self.def_ga_bonus = def_techs["armies"]["bonus"]
        self.def_fleet_lvl = def_techs["fleets"]["level"]
        self.def_fleet_bonus = def_techs["fleets"]["bonus"]
        self.def_lost_cash = self.__int2round(defLostPri)
        self.def_init_power = self.__int2round(defInitPow)
        self.def_lost_power = self.__int2round(defLostPow)
        self.def_perc = (
            defInitPow and [int(100.0*defLostPow/defInitPow)] or [0])[0]


def main():
   pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('%s: break' % os.path.basename(sys.argv[0]))
