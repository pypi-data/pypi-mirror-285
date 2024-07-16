import re

from copy import deepcopy
from typing import Iterator
import csv
from io import StringIO
import logging
import json
import math
import os
from csv2bufr import BUFRMessage

from pymetdecoder import synop as s
import pprint
# synop = "AAXX 01004 88889 12782 61506 10094 20047 30111 40197 53007 60001 81541 333 81656 86070"
# synop = "OOXX RNJ 06204 99233 10853 10035 06514 26/// /3303 10197 20112 39393 40131 5//// 6//// 7//// 8//// 9////   333 55/// ///// 58005 6000/ 83145 81533 81533 444 18031 22053  555 6//// ="
# synop = "OOXX BHO 05194 99210 10799 10119 02522 26/// /3001 10211 2//// 3//// 4//// 5//// 6//// 7//// 8//// 9////   333 55/// ///// 58/// 6000/   555 6//// ="
# synop = "OOXX BHO 05194 99210 10799 10119 02524 26/// /3001 10211 2//// 39765 4//// 5//// 6//// 7//// 8//// 9//// 333 55/// ///// 58/// 6000/   555 6////"
# synop = 'AAXX 21121 \
# 15001 05415 32931 10103 21090 39765 42250 57020 60071 72006 82110 91155 \
#  333 10178 21073 34101 55055 00010 20003 30002 50001 60004 \
#  60035 70500 83145 81533 91008 91111 \
#  444 18031 22053'
# synop = 'OOXX 21121 \
# 15001 07415 32931 10103 21090 39765 42250 57020 60071 72006 82110 91155 \
#  333 10178 21073 34101 45010 54011 55055 00010 20003 30002 50001 60004 \
#  60035 70500 83145 81533 91008 91111 \
#  444 18031 22053='\

# synop = 'OOXX \
#   CGW 13194 99225 10884 10028 ////2 26/// ///// 1//// 2//// 3//// 4//// 5//// 6//// 7//// 8//// 9////   333 55/// ///// 58/// 6000/   555 6////='

# synop = 'OOXX \
#   LAU 13194 99239 10913 09931 ////2 26/// ///// 1//// 2//// 3//// 4//// 5//// 6//// 7//// 8//// 9////   333 55/// ///// 58/// 6000/   555 6//// =\
#   CGW 13194 99225 10884 10028 ////2 26/// ///// 1//// 2//// 3//// 4//// 5////  7//// 8//// 9////   333 55/// ///// 58/// 6000/   555 6////='

# synop = 'OOXX AAATN 18214 99759 50874 56057 12501 46/// /1219 11259 38338 49778 5//// 92100='

# synop = "OOXX BEN 07224 99253 10825 10052 00692 26/// /2404 10137 2//// 3//// 4//// 5//// 6//// 7//// 8//// 9////   333 55/// ///// 58/// 6000/   555 6//// =\
# OOXX BGB 07224 99288 10772 10187 01982 26/// /2602 10113 2//// 3//// 4//// 5//// 6//// 7//// 8//// 9////   333 55/// ///// 58/// 6000/   555 6//// ="

# synop = "OOXX PPD 27184 99172 10821 06472 ////2 26/// ///// 1//// 2//// 3//// 4//// 5//// 6//// 7//// 8//// 9////   333 55/// ///// 58/// 6000/   555 6//// =="
# output = s.SYNOP().decode(synop)
# pprint.pp(output)

LOGGER = logging.getLogger(__name__)

FAILED = 0
PASSED = 1

_keys = ['ship_or_mobile_land_station_id', 'region', 'station_type',
         'year', 'month', 'day', 'hour', 'minute',
         'latitude', 'longitude', 'elevation', 'barometer_elevation', 'station_elevation_quality_mark',
         'station_pressure', 'sea_level_pressure', '3hr_pressure_change',
         'pressure_tendency', '24hr_pressure_change', 'isobaric_surface', 'geopotential_height',
         'air_temperature', 'dewpoint_temperature', 'relative_humidity',
         'visibility', 'precipitation_24hr',
         'cloud_cover', 'cloud_vs_s1', 'cloud_amount_s1', 'lowest_cloud_base',
         'low_cloud_type', 'middle_cloud_type', 'high_cloud_type',
         'low_cloud_drift_direction', 'middle_cloud_drift_direction', 'high_cloud_drift_direction',
         'e_cloud_direction', 'e_cloud_elevation', 'e_cloud_genus',
         'ground_state', 'snow_depth', 'ground_temperature',
         'past_weather_time_period',
         'sunshine_amount_1hr', 'sunshine_amount_24hr',
         'ps1_time_period', 'ps1_amount', 'ps3_time_period', 'ps3_amount',
         'wind_indicator', 'wind_direction', 'wind_speed', 'highest_gust_1', 'highest_gust_2', 'gust_2_time_period',
         'evaporation_instrument', 'evapotranspiration',
         'long_wave_radiation_1hr', 'long_wave_radiation_24hr',
         'short_wave_radiation_1hr', 'short_wave_radiation_24hr',
         'net_radiation_1hr', 'net_radiation_24hr',
         'global_solar_radiation_1hr', 'global_solar_radiation_24hr',
         'diffuse_solar_radiation_1hr', 'diffuse_solar_radiation_24hr',
         'direct_solar_radiation_1hr', 'direct_solar_radiation_24hr',
         'temp_change_time_period', 'temperature_change']

FM14_template = dict.fromkeys(_keys)
THISDIR = os.path.dirname(os.path.realpath(__file__))
MAPPINGS = f"{THISDIR}{os.sep}resources{os.sep}307090_template.json"

# Load template mappings file, this will be updated for each message.
with open(MAPPINGS) as fh:
    _mapping = json.load(fh)

def extract_FM14(data: str) -> list:
    if not data.__contains__("="):
        LOGGER.error((
            "Delimiters (=) are not present in the string"))
        LOGGER.debug(data)
        raise ValueError
    
    start_position = data.find("OOXX")
    if start_position == -1:
        raise ValueError("Invalid FM14 message. 'OOXX' could not be found.")
        
    data = re.split('=', data[start_position:])

    return data[:len(data)-1]


def parse_FM14(message: str, year: int, month: int) -> dict:
    # import pdb; pdb.set_trace()
    message = message.strip()
    LOGGER.debug(f"Parsing message: {message}")
    output = deepcopy(FM14_template)

    decoded = s.SYNOP().decode(message)

    #   ecCodes 001011: ship or mobile land station identifier
    if decoded.get('callsign') is not None:
        output['ship_or_mobile_land_station_id'] = decoded['callsign']['value']

    #   NOTE: Region number has inconsistent documentation in manual and needs to be addressed
    #   ecCodes 001003: WMO Region number
    if decoded.get('region') is not None:
        try:
            output['region'] = decoded['region']['value']
        except Exception:
            output['region'] = None

    #   ecCodes 002001: Type of station
    if decoded.get('weather_indicator') is not None:
        try:
            ix = decoded['weather_indicator']['value']
            if ix <= 3:
                ix_translated = 1  # Manned station
            elif ix == 4:
                ix_translated = 2  # Hybrid station
            elif ix > 4 and ix <= 7:
                ix_translated = 0  # Automatic station
            else:
                ix_translated = None  # Missing value
        except Exception:
            ix_translated = None
    else:
        ix_translated = None  # Missing value

    output['station_type'] = ix_translated

    #   ecCodes 301011: year, month, day / 301012: hour, minute
    output['year'] = year
    output['month'] = month
    if decoded.get('obs_time') is not None:
        try:
            output['day'] = decoded['obs_time']['day']['value']
        except Exception:
            output['day'] = None
        try:
            output['hour'] = decoded['obs_time']['hour']['value']
        except Exception:
            output['hour'] = None

    if decoded.get('exact_obs_time') is not None:
        if decoded['exact_obs_time']['minute'] is not None:
            try:
                output['minute'] = decoded['exact_obs_time']['minute']['value']
            except Exception:
                output['minute'] = 0
        else:
                output['minute'] = 0
        # Overwrite the hour, because the actual observation may be from
        # the hour before but has been rounded in the YYGGiw group
        if decoded['exact_obs_time']['hour'] is not None:
            try:
                output['hour'] = decoded['exact_obs_time']['hour']['value']
            except Exception:
                output['hour'] = None
    else:
        output['minute'] = 0

    if decoded.get('station_position') is not None:
        #   ecCodes 005001/006001: latitude/longitude (high accuracy)
        output['latitude'] = decoded['station_position']['latitude']
        output['longitude'] = decoded['station_position']['longitude']

        #   ecCodes 007030: height of station ground above mean sea level
        if decoded['station_position']['elevation'] is not None:
            output['elevation'] = decoded['station_position']['elevation']['value']

            #   ecCodes 033024: station elevation quality mark
            #   NOTE: KNOWN BUG WITH PYMETDECODER PREVENTING THIS FROM ENCODING QUALITY MARK OF 4 CORRECTLY
            confidence_mark = decoded['station_position']['confidence']
            confidence_units = decoded['station_position']['elevation']['unit']
            if confidence_units == 'm':
                if confidence_mark == 'Excellent':
                    output['station_elevation_quality_mark'] = 1
                elif confidence_mark == 'Good':
                    output['station_elevation_quality_mark'] = 2
                elif confidence_mark == 'Fair':
                    output['station_elevation_quality_mark'] = 3
                elif confidence_mark == 'Poor':
                    output['station_elevation_quality_mark'] = 4
            elif confidence_units == 'ft':
                if confidence_mark == 'Excellent':
                    output['station_elevation_quality_mark'] = 5
                elif confidence_mark == 'Good':
                    output['station_elevation_quality_mark'] = 6
                elif confidence_mark == 'Fair':
                    output['station_elevation_quality_mark'] = 7
                elif confidence_mark == 'Poor':
                    output['station_elevation_quality_mark'] = 8
        else:
            #   Missing elevation information
            output['station_elevation_quality_mark'] = 15
        
        # if decoded['station_position']['elevation']['unit'] == 'm':
        #     match decoded['station_position']['confidence']:
        #         case 'Excellent':
        #             output['station_elevation_quality_mark'] = 1
        #         case 'Good':
        #             output['station_elevation_quality_mark'] = 2
        #         case 'Fair':
        #             output['station_elevation_quality_mark'] = 3
        #         case 'Poor':
        #             output['station_elevation_quality_mark'] = 4
        # elif decoded['station_position']['elevation']['unit'] == 'ft':
        #     match decoded['station_position']['confidence']:
        #         case 'Excellent':
        #             output['station_elevation_quality_mark'] = 5
        #         case 'Good':
        #             output['station_elevation_quality_mark'] = 6
        #         case 'Fair':
        #             output['station_elevation_quality_mark'] = 7
        #         case 'Poor':
        #             output['station_elevation_quality_mark'] = 8

    #   ecCodes 010004: station-level pressure
    if decoded.get('station_pressure') is not None:
        try:
            output['station_pressure'] = round(decoded['station_pressure']['value'] * 100, -1)
        except Exception:
            output['station_pressure'] = None

    #   ecCodes 010051: pressure reduced to mean sea level
    if decoded.get('sea_level_pressure') is not None:
        try:
            output['sea_level_pressure'] = round(decoded['sea_level_pressure']['value'] * 100, -1)
        except Exception:
            output['sea_level_pressure'] = None

    if decoded.get('pressure_tendency') is not None:
        #   ecCodes 010061: 3-hour pressure change
        try:
            output['3hr_pressure_change'] = round(decoded['pressure_tendency']['change']['value'] * 100, -1)
        except Exception:
            output['3hr_pressure_change'] = None

        #   ecCodes 010063: characteristic of pressure tendency
        try:
            output['pressure_tendency'] = decoded['pressure_tendency']['tendency']['value']
        except Exception:
            output['pressure_tendency'] = None

    #   ecCodes 010062: 24-hour pressure change
    if decoded.get('pressure_change') is not None:
        try:
            output['24hr_pressure_change'] = round(decoded['pressure_change']['value']*100, -1)
        except Exception:
            output['24hr_pressure_change'] = None
        
    #   ecCodes 007004: standard-level pressure
    if decoded.get('geopotential') is not None:
        try:
            output['isobaric_surface'] = round(decoded['geopotential']['surface']['value'] * 100, 1)
        except Exception:
            output['isobaric_surface'] = None
        #   ecCodes 010009: Geopotential height
        try:
            output['geopotential_height'] = decoded['geopotential']['height']['value']
        except Exception:
            output['geopotential_height'] = None

    #   ecCodes 012101: air temperature
    if decoded.get('air_temperature') is not None:
        try:
            output['air_temperature'] = round(decoded['air_temperature']['value'] + 273.15, 2)
        except Exception:
            output['air_temperature'] = None

    #   ecCodes 012103: dewpoint temperature
    if decoded.get('dewpoint_temperature') is not None:
        try:
            output['dewpoint_temperature'] = round(decoded['dewpoint_temperature']['value'] + 273.15, 2)
        except Exception:
            output['dewpoint_temperature'] = None

    # Verify that the dewpoint temperature is less than or equal to
    # the air temperature
    if ((output.get('air_temperature') is not None) and
            (output.get('dewpoint_temperature') is not None)):

        A = output['air_temperature']
        D = output['dewpoint_temperature']

        # If the dewpoint temperature is higher than the air temperature,
        # log a warning and set both values to None
        if A < D:
            LOGGER.warning(f"Reported dewpoint temperature {D} is greater than the reported air temperature {A}. Elements set to missing")
            output['air_temperature'] = None
            output['dewpoint_temperature'] = None

    #   ecCodes 013003: reative humidity
    if decoded.get('relative_humidity') is not None:
        try:
            output['relative_humidity'] = decoded['relative_humidity']['value']
        except Exception:
            output['relative_humidity'] = None

    else:
        # if RH is missing estimate from air temperature and dew point
        # temperature
        #
        # Reference to equation / method required
        try:
            A = output['air_temperature']
            D = output['dewpoint_temperature']
        except Exception:
            A = None
            D = None

        if None in (A, D):
            output['relative_humidity'] = None
        else:
            A -= 273.15
            D -= 273.15

            beta = 17.625
            lam = 243.04

            U = 100 * math.exp(((beta*D)/(lam+D)) - ((beta*A)/(lam+A)))

            output['relative_humidity'] = U

    #   ecCodes 020001: horizontal visibility
    if decoded.get('visibility') is not None:
        try:
            output['visibility'] = decoded['visibility']['value']
        except Exception:
            output['visibility'] = None

    #   ecCodes 013023: total precipitation past 24 hours
    if decoded.get('precipitation_24h') is not None:
        # In SYNOP it is given in mm, and in BUFR it is required to be
        # in kg/m^2 (1mm = 1kg/m^2 for water)
        try:
            output['precipitation_24hr'] = decoded['precipitation_24h']['amount']['value'] 
        except Exception:
            output['precipitation_24hr'] = None

    #   ecCodes 020010: Cloud cover (total)
    if decoded.get('cloud_cover') is not None:
        try:
            N_oktas = decoded['cloud_cover']['_code']
            # If the cloud cover is 9 oktas, this means the sky was obscured
            # and we keep the value as None
            if N_oktas == 9:
                N_percentage = 113
            else:
                N_percentage = math.ceil((N_oktas / 8) * 100)
                output['cloud_cover'] = N_percentage
        except Exception:
            output['cloud_cover'] = None

    if decoded.get('cloud_types') is not None:
        #   ecCodes 008002: Vertical significance (surface observations)
        #   ecCodes 020011: cloud amount
        if decoded['cloud_types'].get('low_cloud_amount') is not None:
            try:
                N_oktas = decoded['cloud_types']['low_cloud_amount']['value']
            except Exception:
                N_oktas = None

            #   If the cloud cover is 9 oktas, this means the sky was obscured
            #   By B/C5.4.4.3.1, if sky is obscured, cloud amount shall be reported as 9
            if N_oktas == 9:
                # By B/C5.4.4.2, if sky obscured, use significance code 5
                output['cloud_amount_s1'] = 9
                output['cloud_vs_s1'] = 5
            else:
                # By B/C5.4.4.2, if low clouds present, use significance code 7
                output['cloud_vs_s1'] = 7
                output['cloud_amount_s1'] = N_oktas

        elif decoded['cloud_types'].get('middle_cloud_amount') is not None:
            try:
                N_oktas = decoded['cloud_types']['middle_cloud_amount']['value']
            except Exception:
                N_oktas = None

            #   If the cloud cover is 9 oktas, this means the sky was obscured
            #   By B/C5.4.4.3.1, if sky is obscured, cloud amount shall be reported as 9
            if N_oktas == 9:
                # By B/C5.4.4.2, if sky obscured, use significance code 5
                output['cloud_amount_s1'] = 9
                output['cloud_vs_s1'] = 5
            else:
                # By B/C5.4.4.2, only middle clouds present, use significance
                # code 8
                output['cloud_vs_s1'] = 8
                output['cloud_amount_s1'] = N_oktas

        # According to B/C5.4.4.3.1, if only high clouds present, cloud amount
        # and significance code will be set to 0
        elif decoded['cloud_types']['high_cloud_type'] is not None:
            output['cloud_vs_s1'] = 0
            output['cloud_amount_s1'] = 0

    else:  # Missing values
        output['cloud_vs_s1'] = 63
        output['low_cloud_type'] = 63
        output['middle_cloud_type'] = 63
        output['high_cloud_type'] = 63

    #   ecCodes 020013: Height of base of cloud
    if decoded.get('lowest_cloud_base') is not None:
        try:
            output['lowest_cloud_base'] = round(decoded['lowest_cloud_base']['min'], -1)
        except Exception:
            output['lowest_cloud_base'] = None

    #   ecCodes 020012 x3: cloud type for low, middle, and high cloud groups
    #   We translate these cloud type flags from the SYNOP codes to the
    #   BUFR codes
    if decoded.get('cloud_types') is not None:
        try:
            Cl = decoded['cloud_types']['low_cloud_type']['value'] + 30
        except Exception:
            Cl = None
        output['low_cloud_type'] = Cl

        try:
            Cm = decoded['cloud_types']['middle_cloud_type']['value'] + 20
        except Exception:
            Cm = None

        output['middle_cloud_type'] = Cm

        try:
            Ch = decoded['cloud_types']['high_cloud_type']['value'] + 10
        except Exception:
            Ch = None

        output['high_cloud_type'] = Ch

    #   ecCodes 302005: Cloud layer
    #   DELAYED REPLICATION
            
    #   Create number of s3 group 8 clouds variable, in case there is no group 8
    num_s3_clouds = 0

    if decoded.get('cloud_layer') is not None:

        # Name the array of 8NsChshs groups
        genus_array = decoded['cloud_layer']

        # Get the number of 8NsChshs groups in the SYNOP message
        num_s3_clouds = len(genus_array)

        #   Iterate over cloud groups

        for i in range(num_s3_clouds):

            # The vertical significance is determined by the number of clouds
            # given and whether it is a
            # Cumulonimbus cloud, by B/C5.4.5.2.1. Moreover, it also depends
            # on whether the station is automatic
                
            automatic_state = bool(output['station_type'] == 0)

            #   ecCodes 008002/020012: Vertical significance (surface observations) and Cloud Type
            if genus_array[i] is not None:
                try:
                    C_code = genus_array[i]['cloud_genus']['_code']
                    output[f'cloud_genus_s3_{i+1}'] = C_code

                    if C_code == 9: #   code for cumulonimbus cloud in table 0500
                        if automatic_state:
                            output[f'vs_s3_{i+1}'] = 24
                        else:
                            output[f'vs_s3_{i+1}'] = 4

                    else:  # Non-Cumulonimbus
                        if automatic_state:
                            output[f'vs_s3_{i+1}'] = i+21
                        else:
                            output[f'vs_s3_{i+1}'] = i+1
                except Exception:
                    output[f'vs_s3_{i + 1}'] = None
            else:
                # Missing value
                output[f'cloud_genus_s3_{i+1}'] = None
                if automatic_state:
                    output[f'vs_s3_{i+1}'] = 20
                else:
                    output[f'vs_s3_{i+1}'] = None

            #   ecCodes 020011: Cloud amount
            if genus_array[i]['cloud_cover'] is not None:
            # This is left in oktas just like group 8 in section 1
                try:
                    N_oktas = genus_array[i]['cloud_cover']['value']
                except Exception:
                    N_oktas = None

                #   If the cloud cover is 9 oktas, this means the sky was obscured
                #   By B/C5.4.4.3.1, if sky is obscured, cloud amount shall be reported as 9
                if N_oktas == 9:
                    output[f'cloud_amount_s3_{i+1}'] = 9
                    # Replace vertical significance code in this case
                    output[f'vs_s3_{i+1}'] = 5
                else:
                    output[f'cloud_amount_s3_{i+1}'] = N_oktas
            else:
                # Missing value
                output[f'cloud_amount_s3_{i+1}'] = None

            #   ecCodes 020013: Height of base of cloud
            if genus_array[i]['cloud_height'] is not None:
                # In SYNOP the code table values correspond to heights in m,
                # which BUFR requires
                try:
                    output[f'cloud_height_s3_{i+1}'] = genus_array[i]['cloud_height']['value']
                except Exception:
                    output[f'cloud_height_s3_{i+1}'] = None

    #   ecCodes 302036: Clouds with bases below station level
    #   DELAYED REPLICATION
                        
    #   Initialize number of s4 cloud groups in case there is nothing recorded in group 8
                        
    num_s4_clouds = 0

    if decoded.get('cloud_base_below_station') is not None:

        #   Name the array of NCHHC1 groups
        genus_array = decoded['cloud_base_below_station']

        num_s4_clouds = len(genus_array)

        #   Iterate over cloud groups
        for i in range(num_s4_clouds):

            if genus_array[i] is not None:

                #   ecCodes 008002: Vertical significane (surface observations)
                #   Per B/C5.5.2.1, Code figure 10 will be used for cloud layers
                #   with bases below and tops above station level. Code figure 11
                #   will be used for cloud layers with both bases and tops below station level.

                try:
                    station_level = output['elevation']
                    if genus_array[i]['upper_surface_altitude']['value'] > station_level:
                        output[f'vs_s4_{i+1}'] = 10
                    else:
                        output[f'vs_s4_{i+1}'] = 11
                except Exception:
                    output[f'vs_s4_{i+1}'] = None

                #   ecCodes 020011: Cloud amount
                if genus_array[i]['cloud_cover'] is not None:
                    try:
                        N_oktas = genus_array[i]['cloud_cover']['value']
                        output[f'cloud_amount_s4_{i+1}'] = N_oktas
                    except Exception:
                        #   Missing value
                        output[f'cloud_amount_s4_{i+1}'] = 15

                #   ecCodes 020012: Cloud type
                if genus_array[i]['genus'] is not None:
                    try:
                        C_code = genus_array[i]['genus']['_code']
                        output[f'cloud_genus_s4_{i+1}'] = C_code
                    except Exception:
                        #   Missing value
                        output[f'cloud_genus_s4_{i+1}'] = 63

                #   ecCodes 020014: Height of top of cloud
                if genus_array[i]['upper_surface_altitude'] is not None:
                    try:
                        output[f'cloud_top_height_s4_{i+1}'] = genus_array[i]['upper_surface_altitude']['value']
                    except Exception:
                        output[f'cloud_top_height_s4_{i+1}'] = None

                #   ecCodes 020017: Cloud top description
                if genus_array[i]['description'] is not None:
                    try:
                        output[f'cloud_top_description_s4_{i+1}'] = genus_array[i]['description']['_code']
                    except Exception:
                        output[f'cloud_top_description_s4_{i+1}'] = 15

    #   ecCodes 302047: Direction of cloud drift
                        
    #   ecCodes 008002: Vertical significance (surface observations)
    #   By B/C5.6.1, vertical significance is hard coded to 7, 8, and 9
    #   for the first, second, and third replication. As such, it does not need to be encoded here
                        
    #   ecCodes 020054: True direction from which a phenomenon or clouds are moving or in which they are observed
    #   direction is reported using cardinal directions and their intermediaries (NE, E, SE, S, SW, W, NW, N)
    #   need to convert the direction to a degree bearing
    def to_bearing(direction):
        # Between NE and NW
        if direction < 8:
            return direction * 45
        # N
        if direction == 8:
            return 0
        
    if decoded.get('cloud_drift_direction') is not None:
        if decoded['cloud_drift_direction']['low'] is not None:
            try:
                low_dir = decoded['cloud_drift_direction']['low']['_code']
                #   WMO Code manual table 0700 specifies that direction code of 0
                #   indicates stationary or no clouds and a code of 9 indicates
                #   all directions or unknown/variable. In either case, seems that
                #   it is not appropriate to encode something to bufr
                if low_dir > 0 and low_dir < 9:
                    output['low_cloud_drift_direction'] = to_bearing(low_dir)
                else:
                    output['low_cloud_drift_direction'] = None
            except Exception:
                output['low_cloud_drift_direction'] = None

        if decoded['cloud_drift_direction']['middle'] is not None:
            try:
                middle_dir = decoded['cloud_drift_direction']['middle']['_code']  # noqa
                if middle_dir > 0 and middle_dir < 9:
                    output['middle_cloud_drift_direction'] = to_bearing(middle_dir)  # noqa
                else:
                    output['middle_cloud_drift_direction'] = None
            except Exception:
                output['middle_cloud_drift_direction'] = None

        if decoded['cloud_drift_direction']['high'] is not None:
            try:
                high_dir = decoded['cloud_drift_direction']['high']['_code']
                if high_dir > 0 and high_dir < 9:
                    output['high_cloud_drift_direction'] = to_bearing(high_dir)
                else:
                    output['high_cloud_drift_direction'] = None
            except Exception:
                output['high_cloud_drift_direction'] = None

    #   ecCodes 302048: Direction and elevation of cloud
    if decoded.get('cloud_elevation') is not None:
        #   ecCodes 005021: Bearing or azimuth
        if decoded['cloud_elevation']['direction'] is not None:
            try:
                e_dir = decoded['cloud_elevation']['direction']['_code']
            except Exception:
                e_dir = None

            #   WMO Code manual table 0700 specifies that direction code of 0
            #   indicates stationary or no clouds and a code of 9 indicates
            #   all directions or unknown/variable. In either case, seems that
            #   it is not appropriate to encode something to bufr

            if e_dir > 0 and e_dir < 9:
                # We reuse the to_bearing function from above
                output['e_cloud_direction'] = to_bearing(e_dir)
            else:
                output['e_cloud_direction'] = None

        #   ecCodes 007021: Elevation
        if decoded['cloud_elevation']['elevation'] is not None:
            try:
                output['e_cloud_elevation'] = decoded['cloud_elevation']['elevation']['value']
            except Exception:
                output['e_cloud_elevation'] = None

        #   ecCodes 020012: Cloud type
        if decoded['cloud_elevation']['genus'] is not None:
            try:
                output['e_cloud_genus'] = decoded['cloud_elevation']['genus']['_code']  # noqa
            except Exception:
                output['e_cloud_genus'] = None
        else:
            # Missing value
            output['e_cloud_genus'] = None

    #   ecCodes 307037: State of ground, snow depth, ground minimum temperature
    #   NOTE: Gets encoded differently depending on whether or not snow is on the ground
            
    #   First check for base ground-state information (i.e. no snow on the ground)
    if decoded.get('ground_state') is not None:

        #   ecCodes 020062: State of the ground (with or without snow)

        if decoded['ground_state']['state'] is not None:
            try:
                output['ground_state'] = decoded['ground_state']['state']['value']
            except Exception:
                output['ground_state'] = 31
        else:
            #   Missing value
            output['ground_state'] = 31

        #   ecCodes 012113: Ground minimum temperature, past 12 hours
        if decoded['ground_state']['temperature'] is not None:
            try:
                #  Convert to Kelvin for bufr
                output['ground_temperature'] = round(decoded['ground_state']['temperature']['value'] + 273.15, 2)
            except Exception:
                output['ground_temperature'] = None
            
    #   Then check for whether snow is on the ground and encode according to those values    
    if decoded.get('ground_state_snow') is not None:

        #   ecCodes 020062: State of the ground (with or without snow)

        if decoded['ground_state_snow']['state'] is not None:
            #   We translate the ground state flags from the SYNOP codes to the
            #   BUFR codes. Values for state of the ground with snow or ice
            #   cover start at entry 10 in WMO Code Table 0975
            try:
                state = decoded['ground_state_snow']['state']['value']
                if state is not None:
                    output['ground_state'] = state + 10
                else:
                    output['ground_state'] = 31
            except Exception:
                output['ground_state'] = 31
        else:  # Missing value
            output['ground_state'] = 31
            
        #   ecCodes 013013: Total Snow Depth
        if decoded['ground_state_snow']['depth'] is not None:
            try:
                snow_depth = decoded['ground_state_snow']['depth']['depth']  # noqa
            except Exception:
                snow_depth = None
            #   depth is reported in cm. Need to convert to m for bufr
            if snow_depth is not None:
                output['snow_depth'] = snow_depth * 0.01
            else:
                output['snow_depth'] = None
        
    #   ecCodes 302043: Basic synoptic "period" data
    #   ecCodes 302038: Present and past weather
    #   ecCodes 020003: Present weather
    #   NOTE: Will come back to this once I hear back from Rory and/or pymetdecoder devs

    #   ecCodes 004024: Time period for past weather (hrs)
    #   The past weather time period is determined by the hour of observation,
    #   as per B/C5.10.1.7.1 and B/C5.10.1.8.1
    hr = output['hour']

    #   NOTE: All time periods must be negative
    if hr % 6 == 0:
        output['past_weather_time_period'] = -6
    elif hr % 3 == 0:
        output['past_weather_time_period'] = -3
    elif hr % 2 == 0:
        output['past_weather_time_period'] = -2
    else:
        output['past_weather_time_period'] = -1

    #   ecCodes 302039 (x2): Sunshine data from 1 hour and 24 hour period

    #   ecCodes 004024: Time periods for sunshine observation              
    #   First replication for one hour, second replication for 24 hour
    #   004004 always coded as -1 for one hour in first replication and
    #   -24 for 24 hours in second replication
                
    #   ecCodes 014031: Total Sunshine
    if decoded.get('sunshine') not in [None, [None]]:
        if decoded['sunshine'][0].get('amount') is not None:

            try:
                sun_time = decoded['sunshine'][0].get('duration')['value']
            except Exception:
                sun_time = None

            #   sunshine amount is recorded in hours. Need to convert to minutes for bufr
            try:
                sun_amount = decoded['sunshine'][0].get('amount')['value'] * 60
            except Exception:
                sun_amount = None
            if sun_time == 1:
                output['sunshine_amount_1hr'] = sun_amount
            elif sun_time == 24:
                output['sunshine_amount_24hr'] = sun_amount
    
    #   eccodes 302040: Precipitation measurement
    #   ecCodes 004024/013011: Time period/Total precipitation or total water equivalent
    #   004024/013011 repeated 2x, regional in first replication and national in second
    #   Section 1 precipitation data is encoded in first replication
    if decoded.get('precipitation_s1') is not None:
        #   Time period shall be reported as a negative value in hours
        try:
            output['ps1_time_period'] = decoded['precipitation_s1']['time_before_obs']['value'] * -1
        except Exception:
            output['ps1_time_period'] = None

        try:
            output['ps1_amount'] = decoded['precipitation_s1']['amount']['value']
        except Exception:
            output['ps1_amount'] = None
                
    #   Section 3 precipitation data encoded in second replication
    if decoded.get('precipitation_s3') is not None:
        try:
            output['ps3_time_period'] = decoded['precipitation_s3']['time_before_obs']['value'] * -1
        except Exception:
            output['ps3_time_period'] = None

        try:
            output['ps3_amount'] = decoded['precipitation_s3']['amount']['value']
        except Exception:
            output['ps3_amount'] = None
                
    #   ecCodes 302041: Extreme temperature data
    #   NOTE: Have to come back to this after discussing regional rules and addressing the region no. problem
            
    #   ecCodes 302042: Wind Data
    #   ecCodes 002002: Type of instrumentation for wind measurement
    if decoded.get('wind_indicator') is not None:
        try:
            iw = decoded['wind_indicator']['value']

            # Note bit 3 should never be set for synop, units
            # of km/h not reportable
            if iw == 0:
                iw_translated = 0b0000  # Wind in m/s, default, no bits set
            elif iw == 1:
                iw_translated = 0b1000  # Wind in m/s with anemometer bit 1 (left most) set  # noqa
            elif iw == 3:
                iw_translated = 0b0100  # Wind in knots, bit 2 set
            elif iw == 4:
                iw_translated = 0b1100  # Wind in knots with anemometer, bits
            else:
                iw_translated = None  # 0b1111  # Missing value

            output['wind_indicator'] = iw_translated
        except Exception:
            output['wind_indicator'] = None

    #   ecCodes 008021: Time significance
    #   Value hard coded to 2 for time averaged
            
    #   ecCodes 004025: Time period or displacement (min)
    #   Value hard coded to -10 for  preceding 10 minute period
            
    if decoded.get('surface_wind') is not None:

        #   ecCodes 011001: Wind direction
        try:
            output['wind_direction'] = decoded['surface_wind']['direction']['value']  # noqa
        except Exception:
            output['wind_direction'] = None

        #   ecCodes 011002: Wind speed
        try:
            ff = decoded['surface_wind']['speed']['value']
            ff_unit = decoded['wind_indicator']['unit']

            #   convert to m/s if reported units are KTs
            if ff_unit == 'KT':
                ff *= 0.51444
            output['wind_speed'] = ff
        except Exception:
            output['wind_speed'] = None
            
    if decoded.get('highest_gust') is not None:

        #   ecCodes 004025: Time period or displacement (in minutes)
        #   First replication hard coded to -10 to represent preceding 10 minute period

        #   ecCodes 011041: Maximum wind gust speed
        #   First replication encoding the gusts from previous 10-minute period
        try:
            #   convert to m/s if reported units are KTs
            ff = decoded['highest_gust'][0]['speed']['value']
            ff_unit = decoded['highest_gust'][0]['speed']['unit']
            if ff_unit == 'KT':
                ff *= 0.51444
            output['highest_gust_1'] = ff
        except Exception:
            output['highest_gust_1'] = None

        #   ecCodes 004025: Time period or displacement (in minutes)
        #   second replication is for time period covering the same span as past weather period
        #   NOTE: past weather time period is reported in hours. Need to convert to minutes
        output['gust_2_time_period'] = output['past_weather_time_period'] * 60
            
        #   ecCodes 011041 Maximum wind gust speed
        #   second replication is for time period covering the same span as past weather period
        try:
            #   convert to m/s if reported units are KTs
            ff = decoded['highest_gust'][1]['speed']['value']
            ff_unit = decoded['highest_gust'][1]['speed']['unit']
            if ff_unit == 'KT':
                ff *= 0.51444
            output['highest_gust_2'] = ff
        except Exception:
            output['highest_gust_2'] = None   
    
    #   ecCodes 302044: Evaporation Data
    #   ecCodes 004024: Time period or displacement
    #   Value hard coded as -24 for previous 24 hour period
    
    if decoded.get('evapotranspiration') is not None:

        #   ecCodes 002004: Type of instrumentation for evaporation measurement
        try:
            output['evaporation_instrument'] = decoded['evapotranspiration']['type']['_code']
        except Exception:
            #   missing value
            output['evaporation_instrument'] = 15

        #   ecCodes 013033: Evaporation/evapotranspiration
        try:
            output['evapotranspiration'] = decoded['evapotranspiration']['amount']['value']
        except Exception:
            output['evapotranspiration'] = None

    #   ecCodes 302045 (x2): Radiation data from 1 and 24 hr period
    #   First replication encodes 1 hr period, second replication encodes 24 hr
            
    #   ecCodes 004024: Time period or displacement (hrs)
    #   Hard coded to -1 in first replication and -24 in second replication
            
    if decoded.get('radiation') is not None:
        rad_dict = decoded['radiation']
        # NOTE: If the radiation is over the past hour, it is given in kJ/m^2.
        # If it is over the past 24 hours, it is given in J/cm^2.
        # Create a function to do the appropriate conversion depending
        # on time period

        def rad_convert(rad, time):
            if time == 1:
                # 1 kJ/m^2 = 1000 J/m^2
                return 1000 * rad
            elif time == 24:
                # 1 J/cm^2 = 10000 J/m^2
                return 10000 * rad
            
        #   ecCodes 014002: Long-wave radiation, integrated
        if 'downward_long_wave' in rad_dict:
            try:
                rad = rad_dict['downward_long_wave'][0]['value']
                time = rad_dict['downward_long_wave'][0]['time_before_obs']['value']
            except Exception:
                rad = None
                time = None

            if None not in (rad, time):
                if time == 1:
                    #  Set positive and convert to J/m^2,rounding to 10000s
                    # of J/m^2 (B/C5.12.2)
                    output['long_wave_radiation_1hr'] = min(round(rad_convert(rad, time), -4), 6.5535e+07)
                elif time == 24:
                    #  Set positive and convert to J/m^2,rounding to 10000s
                    # of J/m^2 (B/C5.12.2)
                    output['long_wave_radiation_24hr'] = min(round(rad_convert(rad, time), -4), 6.5535e+07)

        if 'upward_long_wave' in rad_dict:
            try:
                rad = rad_dict['upward_long_wave'][0]['value']
                time = rad_dict['upward_long_wave'][0]['time_before_obs']['value']
            except Exception:
                rad = None
                time = None

            if None not in (rad, time):
                if time == 1:
                    #  Set negative and convert to J/m^2,rounding to 10000s
                    # of J/m^2 (B/C5.12.2)
                    output['long_wave_radiation_1hr'] = max(-1 * round(rad_convert(rad, time), -4), -6.5536e+07)
                elif time == 24:
                    #  Set negative and convert to J/m^2,rounding to 10000s
                    # of J/m^2 (B/C5.12.2)
                    output['long_wave_radiation_24hr'] = max(-1 * round(rad_convert(rad, time), -4), -6.5536e+07)

        #   ecCodes 014004: Short-wave radiation, integrated
        if 'short_wave' in rad_dict:
            try:
                rad = rad_dict['short_wave'][0]['value']
                time = rad_dict['short_wave'][0]['time_before_obs']['value']
            except Exception:
                rad = None
                time = None

            if None not in (rad, time):
                if time == 1:
                    #  Convert to J/m^2,rounding to 1000s of J/m^2 (B/C5.12.2)
                    output['short_wave_radiation_1hr'] = min(round(rad_convert(rad, time), -3), 6.5535e+07)
                if time == 24:
                    #  Convert to J/m^2,rounding to 1000s of J/m^2 (B/C5.12.2)
                    output['short_wave_radiation_24hr'] = min(round(rad_convert(rad, time), -3), 6.5535e+07)

        #   ecCodes 014016: Net radiation, integrated
        if 'positive_net' in rad_dict:
            try:
                rad = rad_dict['positive_net'][0]['value']
                time = rad_dict['positive_net'][0]['time_before_obs']['value']
            except Exception:
                rad = None
                time = None
            if None not in (rad, time):
                if time == 1:
                    #  Convert to J/m^2,rounding to 1000s of J/m^2 (B/C5.12.2)
                    output['net_radiation_1hr'] = round(rad_convert(rad, time), -3)
                elif time == 24:
                    #  Convert to J/m^2,rounding to 1000s of J/m^2 (B/C5.12.2)
                    output['net_radiation_24hr'] = round(rad_convert(rad, time), -3)

        if 'negative_net' in rad_dict:
            try:
                rad = rad_dict['negative_net'][0]['value']
                time = rad_dict['negative_net'][0]['time_before_obs']['value']
            except Exception:
                rad = None
                time = None

            if None not in (rad, time):
                if time == 1:
                    #  Set negative and convert to J/m^2,rounding to 1000s
                    # of J/m^2 (B/C5.12.2)
                    output['net_radiation_1hr'] = -1 * round(rad_convert(rad, time), -3)
                elif time == 24:
                    #  Set negative and convert to J/m^2,rounding to 1000s
                    # of J/m^2 (B/C5.12.2)
                    output['net_radiation_24hr'] = -1 * round(rad_convert(rad, time), -3)

        #   ecCodes 014028: Global radiation (high accuracy), integrated
        if 'global_solar' in rad_dict:
            try:
                rad = rad_dict['global_solar'][0]['value']
                time = rad_dict['global_solar'][0]['time_before_obs']['value']
            except Exception:
                rad = None
                time = None

            if None not in (rad, time):
                if time == 1:
                    #  Convert to J/m^2,rounding to 100s of J/m^2 (B/C5.12.2)
                    output['global_solar_radiation_1hr'] = round(rad_convert(rad, time), -2)
                elif time == 24:
                    #  Convert to J/m^2,rounding to 100s of J/m^2 (B/C5.12.2)
                    output['global_solar_radiation_24hr'] = round(rad_convert(rad, time), -2)

        #   ecCodes 014029: Diffuse radiation (high accuracy), integrated
        if 'diffused_solar' in rad_dict:
            try:
                rad = rad_dict['diffused_solar'][0]['value']
                time = rad_dict['diffused_solar'][0]['time_before_obs']['value']
            except Exception:
                rad = None
                time = None

            if None not in (rad, time):
                if time == 1:
                    #  Convert to J/m^2,rounding to 100s of J/m^2 (B/C5.12.2)
                    output['diffuse_solar_radiation_1hr'] = round(rad_convert(rad, time), -2)
                elif time == 24:
                    #  Convert to J/m^2,rounding to 100s of J/m^2 (B/C5.12.2)
                    output['diffuse_solar_radiation_24hr'] = round(rad_convert(rad, time), -2)

        #   ecCodes 014030: Direct radiation (high accuracy), integrated
        if 'direct_solar' in rad_dict:
            try:
                rad = rad_dict['direct_solar'][0]['value']
                time = rad_dict['direct_solar'][0]['time_before_obs']['value']  # noqa
            except Exception:
                rad = None
                time = None

            if None not in (rad, time):
                if time == 1:
                    #  Convert to J/m^2,rounding to 100s of J/m^2 (B/C5.12.2)
                    output['direct_solar_radiation_1hr'] = round(rad_convert(rad, time), -2)  # noqa
                elif time == 24:
                    #  Convert to J/m^2,rounding to 100s of J/m^2 (B/C5.12.2)
                    output['direct_solar_radiation_24hr'] = round(rad_convert(rad, time), -2)  # noqa

    #   ecCodes 302046: Temperature Change
    #   ecCodes 004024 (x2): Time period or displacement (hrs)
    #   First replication corresponds to period covered by past weather
    #   Second replication specifies time of occurence of temperature change
                    
    if decoded.get('temperature_change') is not None:

        try:
            output['temp_change_time_period'] = decoded['temperature_change']['time_before_obs']['value'] * -1
        except Exception:
            output['temp_change_time_period'] = None

        #   ecCodes 012049: Temperature change over specified period
        #   reported in degrees C, need to convert to Kelvin for bufr
        if decoded['temperature_change']['change'] is not None:
            try:
                output['temperature_change'] = decoded['temperature_change']['change']['value']
            except Exception:
                output['temperature_change'] = None

    return output, num_s3_clouds, num_s4_clouds

def update_data_mapping(mapping: list, update: dict):
    match = False
    for idx in range(len(mapping)):
        if mapping[idx]['eccodes_key'] == update['eccodes_key']:
            match = True
            break
    if match:
        mapping[idx] = update
    else:
        mapping.append(update)
    return mapping

def transform(data: str, year: int, month: int) -> Iterator[dict]:

    try:
        # is_bulletin = False
        messages = extract_FM14(data)
        # if messages[0][:5] == 'OOXX\n':
        #     LOGGER.debug("File is FM14 bulletin")
        #     is_bulletin = True
    except Exception as e:
        LOGGER.error(e)
        return None
    
    # Count how many conversions were successful using a dictionary
    conversion_success = {}

    print(messages)
    # print(f"Is bulletin: {is_bulletin}")
    
    for fm14 in messages:
        result = dict()

        mapping = deepcopy(_mapping)

        try:
            if fm14[:4] == 'OOXX':
                msg, num_s3_clouds, num_s4_clouds = parse_FM14(fm14, year, month)
            else:
                msg, num_s3_clouds, num_s4_clouds = parse_FM14(f"OOXX {fm14}", year, month)
            tsi = msg['ship_or_mobile_land_station_id']
            # pprint.pp(msg)

        except Exception as e:
            LOGGER.error(f"Error parsing FM14 report: {fm14}. {str(e)}")

        #   Before adding cloud mappings to the existing template structure, some existing instances of particular descriptors that are
        #   used in section 3 and section 4 cloud groups need to be incremented based on the number of replications
        #   Specifically these descriptors need to be incremented:
        #   -verticalSignificanceSurfaceObservations, starting from the 4th iteration
        #   -cloudAmount, starting from the 4th iteration
        #   -cloudType, starting from the 6th iteration
        #   -heightOfBaseOfCloud, starting from the 3rd iteration
        #   -heightOfTopOfCloud, starting from the 2nd iteration
        #   -cloudTopDescription, starting from the 2nd iteration
        
        for idx in range(len(mapping['data'])):
            descriptor_info = re.split('#', mapping['data'][idx]['eccodes_key'])
            itr = int(descriptor_info[1])
            descriptor = descriptor_info[2]
            if descriptor == 'verticalSignificanceSurfaceObservations':
                if itr >= 4:
                    mapping['data'][idx] = {"eccodes_key": f"#{itr+num_s3_clouds+num_s4_clouds-2}#verticalSignificanceSurfaceObservations", "value": f"{mapping['data'][idx]['value']}"}
            elif descriptor == 'cloudAmount':
                if itr >= 4:
                    mapping['data'][idx] = {"eccodes_key": f"#{itr+num_s3_clouds+num_s4_clouds-2}#cloudAmount", "value": f"{mapping['data'][idx]['value']}"}
            elif descriptor == 'cloudType':
                if itr >= 6:
                    mapping['data'][idx] = {"eccodes_key": f"#{itr+num_s3_clouds+num_s4_clouds-2}#cloudType", "value": f"{mapping['data'][idx]['value']}"}
            elif descriptor == 'heightOfBaseOfCloud':
                if itr >= 3:
                    mapping['data'][idx] = {"eccodes_key": f"#{itr+num_s3_clouds+num_s4_clouds-2}#heightOfBaseOfCloud", "value": f"{mapping['data'][idx]['value']}"}
            elif descriptor == 'heightOfTopOfCloud':
                if itr >= 2:
                    mapping['data'][idx] = {"eccodes_key": f"#{itr+num_s3_clouds+num_s4_clouds-2}#heightOfTopofCloud", "value": f"{mapping['data'][idx]['value']}"}
            elif descriptor == 'cloudTopDescription':
                if itr >= 2:
                    mapping['data'][idx] = {"eccodes_key": f"#{itr+num_s3_clouds+num_s4_clouds-2}#cloudTopDescription", "value": f"{mapping['data'][idx]['value']}"}

        #   create mappings for section 3 cloud layers
        #   verticalSignificanceSurfaceObservations used 1 previous time
        #   cloudAmount used 1 previous time
        #   cloudType used 3 previous times
        #   heightOfBaseofCloud used 1 previous time
        for idx in range(num_s3_clouds):
            s3_cloud_mappings = [
                {"eccodes_key": f"#{idx+2}#verticalSignificanceSurfaceObservations", "value": f"data:vs_s3_{idx+1}"},
                {"eccodes_key": f"#{idx+2}#cloudAmount", "value": f"data:cloud_amount_s3_{idx+1}"},
                {"eccodes_key": f"#{idx+4}#cloudType", "value": f"data:cloud_genus_s3_{idx+1}"},
                {"eccodes_key": f"#{idx+2}#heightOfBaseOfCloud", "value": f"data:cloud_height_s3_{idx+1}"}
            ]
            for m in s3_cloud_mappings:
                mapping['data'] = update_data_mapping(mapping['data'], m)

        #   create mappings for section 4 clouds with bases below station level
        for idx in range(num_s4_clouds):
            #   Per B/C5.5.2.1, Code figure 10 will be used for cloud layers
            #   with bases below and tops above station level. Code figure 11
            #   will be used for cloud layers with both bases and tops below station level.
            cloud_top_height = msg[f'cloud_top_height_s4_{idx+1}']
            if cloud_top_height > int(msg['elevation']):
                vs_s4 = 10
            else:
                vs_s4 = 11

            #   verticalSignificanceSurfaceObservations used 1 previous time plus the number of s3 cloud groups
            #   cloudAmount used 1 previuos time plus the number of s3 cloud groups
            #   cloudType used 3 previous times plus the number of s3 cloud groups
            #   heightOfTopOfCloud not used previously
            #   cloudTopDescription not used previously
                
            s4_cloud_mappings = [
                {"eccodes_key": f"#{idx+2+num_s3_clouds}#verticalSignificanceSurfaceObservations", "value": f"const:{vs_s4}"},
                {"eccodes_key": f"#{idx+2+num_s3_clouds}#cloudAmount", "value": f"data:cloud_amount_s4_{idx+1}"},
                {"eccodes_key": f"#{idx+4+num_s3_clouds}#cloudType", "value": f"data:cloud_genus_s4_{idx+1}"},
                {"eccodes_key": f"#{idx+1}#heightOfTopOfCloud", "value": f"data:cloud_top_height_s4_{idx+1}"},
                {"eccodes_key": f"#{idx+1}#cloudTopDescription", "value": f"data:cloud_top_description_s4_{idx+1}"}
            ]

            for m in s4_cloud_mappings:
                mapping['data'] = update_data_mapping(mapping['data'], m)

        #   set number of replications for each group
        ns3cld_302005 = num_s3_clouds
        ns4cld_302036 = num_s4_clouds

        unexpanded_descriptors = [307090]
        short_delayed_replications = []
        delayed_replications = [ns3cld_302005, ns4cld_302036]
        extended_delayed_replications = []
        table_version = 37
        
        try:
            # create new BUFR msg
            message = BUFRMessage(
                unexpanded_descriptors,
                short_delayed_replications,
                delayed_replications,
                extended_delayed_replications,
                table_version)
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error("Error creating BUFRMessage")
            continue

        #   Attempt to parse the message into the bufr template mapping
        try:
            message.parse(msg, mapping)
            conversion_success[tsi] = True
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error("Error parsing message")
            conversion_success[tsi] = False

        # Only convert to BUFR if there's no errors so far
        if conversion_success[tsi]:
            try:
                result["bufr4"] = message.as_bufr()  # encode to BUFR
                status = {"code": PASSED}
            except Exception as e:
                LOGGER.error("Error encoding BUFR, null returned")
                LOGGER.error(e)
                result["bufr4"] = None
                status = {
                    "code": FAILED,
                    "message": f"Error encoding, BUFR set to None:\n\t\tError: {e}\n\t\tMessage: {msg}"  # noqa
                }
                conversion_success[tsi] = False
        
            # now identifier based on callsign and observation date as identifier
            isodate = message.get_datetime().strftime('%Y%m%dT%H%M%S')
            rmk = f"CALLSIGN_{tsi}_{isodate}"

            # now additional metadata elements
            result["_meta"] = {
                "id": rmk,
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        message.get_element('#1#longitude'),
                        message.get_element('#1#latitude')
                    ]
                },
                "properties": {
                    "md5": message.md5(),
                    "wigos_station_identifier": f"0-20009-0-{message.get_element('#1#shipOrMobileLandStationIdentifier')}",
                    "datetime": message.get_datetime(),
                    "originating_centre":
                    message.get_element("bufrHeaderCentre"),
                    "data_category": message.get_element("dataCategory")
                },
                "result": status,
                "template": 307090
            }

        # now yield result back to caller
        yield result

        # Output conversion status to user
        if conversion_success[tsi]:
            LOGGER.info(f"Station {tsi} report converted")
        else:
            LOGGER.info(f"Station {tsi} report failed to convert")

    # calculate number of successful conversions
    conversion_count = sum(tsi for tsi in conversion_success.values())
    # print number of messages converted
    LOGGER.info((f"{conversion_count} / {len(messages)}"
            " reports converted successfully"))

# result = transform(synop, 2024, 3)

# for item in result:
#     print(item)
#     bufr4 = item['bufr4']

# f = open('bufrtest.bufr','wb')
# f.write(bufr4)
# f.close()












# unexpanded_descriptors = [307090]
# short_delayed_replications = []
# delayed_replications = []
# extended_delayed_replications = []
# table_version = 37

# message = BUFRMessage(
#     unexpanded_descriptors,
#     short_delayed_replications,
#     delayed_replications,
#     extended_delayed_replications,
#     table_version)