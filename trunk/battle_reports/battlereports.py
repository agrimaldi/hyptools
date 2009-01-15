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
BOMB_RGX = re.compile(
    r"()")


class Analysis(dict):
    """
    Wrapper for the BattleReport class.
    This class is used to analyse several battle reports in a row.
    Battle reports are stored as a dictionary whose keys are the name of the
    planet, and the values are BattleReport objects.
    """
    def __init__(self, raw_data=None):
        self.__parse(raw_data.replace('\r', ''))

    def __parse(self, input_str):
        """
        Parse the data and returns a dictionary
            dict[BattleReport.name] = BattleReport.nice_report
        """
        start_indexes = [m.start() for m in DATE_RGX.finditer(input_str)]
        end_indexes = [i-5 for i in start_indexes[1:]] + [None]
        list_report = [BattleReport(input_str[start:end])
                        for start, end in zip(start_indexes, end_indexes)]
        for bt in list_report:
            if bt.name not in self:
                self[bt.name] = [bt.nice_report]
            else:
                self[bt.name].append(bt.nice_report)


class BattleReport:
    """
    Battle Report class.
    Contains information about a single battle report on a single planet.
    Use the wrapper Analysis to analyse several battle reports in a raw.
        - raw_battle_report = input string, supposed to be a battle report
        - atk = dictionary containing information about the attacker's fleets
        - def = dictionary containing information about the defender's fleets
        - date = date and hour the battle tick happened
        - name = name of the planet the battle tick happened on
    """
    def __init__(self, raw_battle_report=None):
        self.raw_battle_report = raw_battle_report
        self.atk_units = {}
        self.def_units = {}
        self.atk_techs = {
            "armies":   {
                "bonus":    '0',
                "level":    "N/A"
            },
            "fleets":   {
                "bonus":    '0',
                "level":    "N/A"}
        }
        self.def_techs = {
            "armies":   {
                "bonus":    '0',
                "level":    "N/A"
            },
            "fleets":   {
                "bonus":    '0',
                "level":    "N/A"}
        }
        self.date = ""
        self.name = ""
        self.__parse()
        self.nice_report = self.__reformat()

    def __int2round(self, num):
        """
        This method converts an integer to a rounded string :
        3800000 --> 3.8M
            __int2round(3800000) returns "3.8M"
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
        Converts strings such as "3.8M" to the corresponding integer value :
        3.8M --> 3800000
            round2int("3.8M") returns 3800000
        """
        if rnum.endswith('M', -1):
            return int(float(rnum[:-1]) * 1000000)
        else:
            return int(rnum)

    def __parse(self):
        """
        Single battle report parsing method.
        The method populates the dictionnaries self.atk_units and self.def_units
        with the number and type of ships initially owned and lost during the
        battle tick by both sides.
        """
        try:
            match = REGX.search(self.raw_battle_report)
            self.date = match.group("date")
            self.name = match.group("name")
            fleets = FLEET_RGX.findall(self.raw_battle_report)
            techs = TECH_RGX.findall(self.raw_battle_report)
        except:
            sys.exit("\n\nFailed to parse battle report\n\n")
        else:
            for techdata in techs:
                sup = {
                    "bonus": techdata[0],
                    "level": techdata[3]
                }
                inf = {
                    "bonus": '0',
                    "level": techdata[4]
                }
                if techdata[1] == "defending":
                    self.def_techs[techdata[2]] = sup
                    self.atk_techs[techdata[2]] = inf
                elif techdata[1] == "attacking":
                    self.atk_techs[techdata[2]] = sup
                    self.def_techs[techdata[2]] = inf
            for ship in fleets:
                self.def_units[ship[0]] = {
                    "init": ship[3],
                    "lost": ship[4]
                }
                self.atk_units[ship[0]] = {
                    "init": ship[5],
                    "lost": ship[6]
                }

    def __reformat(self):
        """
        This method does all necessary computations and returns a reformated
        battle report.
        """
        atkInitPow = 0
        atkLostPow = 0
        atkLostPri = 0
        defInitPow = 0
        defLostPow = 0
        defLostPri = 0

        report = """
Battle report for planet <b>$name</b>
<b>$date</b>
<pre>
<b>Attacking :</b>
                    Initial         Lost
"""
        for unit, amount in self.atk_units.iteritems():
            report = ''.join([report,
                              unit,
                              amount['init'].rjust(27-len(unit)),
                              amount['lost'].rjust(13), '\n'])
            if unit != "Ground Armies" and unit != "Carried Armies":
                atkInitPow += self.__round2int(amount['init']) * POWER[unit]
                atkLostPow += self.__round2int(amount['lost']) * POWER[unit]
                atkLostPri += self.__round2int(amount['lost']) * PRICE[unit]

        report += """TL GAs :    <b>$atk_ga_lvl</b>\t(+$atk_ga_bonus%)
TL Ships :  <b>$atk_fleet_lvl</b>\t(+$atk_fleet_bonus%)

<b>Defending :</b>
                    Initial         Lost
"""
        for unit, amount in self.def_units.iteritems():
            report = ''.join([report,
                              unit,
                              amount['init'].rjust(27-len(unit)),
                              amount['lost'].rjust(13), '\n'])
            if unit != "Ground Armies" and unit != "Carried Armies":
                defInitPow += self.__round2int(amount['init']) * POWER[unit]
                defLostPow += self.__round2int(amount['lost']) * POWER[unit]
                defLostPri += self.__round2int(amount['lost']) * PRICE[unit]

        report += """TL GAs :    <b>$def_ga_lvl</b>\t(+$def_ga_bonus%)
TL Ships :  <b>$def_fleet_lvl</b>\t(+$def_fleet_bonus%)
</pre>--------------------------------
<b>Summary :</b>
<pre>
<b>Attacking :</b>
Lost cash :     $atk_lost_cash
Initial AvP :   $atk_init_power
Lost AvP :      $atk_lost_power
Losses of       <b>$atk_perc%</b>

<b>Defending :</b>
Lost cash :     $def_lost_cash
Initial AvP :   $def_init_power
Lost AvP :      $def_lost_power
Losses of       <b>$def_perc%</b></pre>"""
        brTemplate = string.Template(report)
        nice_battle_report = brTemplate.substitute({
            "name":             self.name,
            "date":             self.date,
            "atk_ga_lvl":       self.atk_techs["armies"]["level"],
            "atk_ga_bonus":     self.atk_techs["armies"]["bonus"],
            "atk_fleet_lvl":    self.atk_techs["fleets"]["level"],
            "atk_fleet_bonus":  self.atk_techs["fleets"]["bonus"],
            "atk_lost_cash":    self.__int2round(atkLostPri),
            "atk_init_power":   self.__int2round(atkInitPow),
            "atk_lost_power":   self.__int2round(atkLostPow),
            "atk_perc":         (
                atkInitPow and [int(100.0*atkLostPow / atkInitPow)] or [0])[0],
            "def_ga_lvl":       self.def_techs["armies"]["level"],
            "def_ga_bonus":     self.def_techs["armies"]["bonus"],
            "def_fleet_lvl":    self.def_techs["fleets"]["level"],
            "def_fleet_bonus":  self.def_techs["fleets"]["bonus"],
            "def_lost_cash":    self.__int2round(defLostPri),
            "def_init_power":   self.__int2round(defInitPow),
            "def_lost_power":   self.__int2round(defLostPow),
            "def_perc":         (
                defInitPow and [int(100.0*defLostPow / defInitPow)] or [0])[0]
        })

        return nice_battle_report.strip()


def main():
    s="""2009-01-12 06:30:44
Planet Kadena


Own forces

Defending

Attacking
	Initial	Lost	Initial	Lost	Initial	Lost
Cruisers 	3952 	0 	0 	0 	3952 	0
Destroyers 	3881 	0 	0 	0 	3881 	0
Bombers 	2478 	0 	0 	0 	2478 	0
Scouts 	207041 	0 	0 	0 	207041 	0
Ground Armies 	383 	3 	11 	11 	383 	3
Techno bonus 15% for attacking armies (3>2).
Defenders fought with the energy of despair.



2009-01-12 04:31:05
Planet Kadena


Own forces

Defending

Attacking
	Initial	Lost	Initial	Lost	Initial	Lost
Cruisers 	3952 	0 	0 	0 	3952 	0
Destroyers 	3881 	0 	0 	0 	3881 	0
Bombers 	2478 	0 	0 	0 	2478 	0
Scouts 	207041 	0 	0 	0 	207041 	0
Ground Armies 	400 	17 	60 	49 	400 	17
Techno bonus 15% for attacking armies (3>2).
Defenders fought with the energy of despair.



2009-01-12 04:31:05
Planet Leep


Own forces

Defending

Attacking
	Initial	Lost	Initial	Lost	Initial	Lost
Cruisers 	0 	0 	0 	0 	18942 	39
Destroyers 	0 	0 	0 	0 	11756 	303
Bombers 	1400 	1400 	1400 	1400 	12100 	0
Scouts 	0 	0 	0 	0 	34152 	0
Carried Armies 	0 	0 	0 	0 	? 	6
Ground Armies 	490 	162 	490 	162 	0 	0
Techno bonus 30% for attacking fleets (21.09>0)."""

    a=Analysis(s)
    print a.items()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('%s: break' % os.path.basename(sys.argv[0]))
