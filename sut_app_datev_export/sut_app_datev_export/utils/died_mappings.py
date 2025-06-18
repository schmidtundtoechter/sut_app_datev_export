import frappe
from frappe import _
from datetime import datetime

def get_birth_country_mapping():
    """Returns the mapping for birth countries (DIED 4214)"""
    # This maps directly from Personalerfassungsbogen geburtsland options to DIED codes
    country_mapping = {
        'deutschland': '0',
        'albanien': '121',
        'bosnien und herzegowina': '122',
        'andorra': '123',
        'belgien': '124',
        'bulgarien': '125',
        'dänemark': '126',
        'estland': '127',
        'finnland': '128',
        'frankreich': '129',
        'kroatien': '130',
        'slowenien': '131',
        'serbien und montenegro': '132',
        'serbien (einschl. kosovo)': '133',
        'griechenland': '134',
        'irland': '135',
        'island': '136',
        'italien': '137',
        'jugoslawien': '138',
        'lettland': '139',
        'montenegro': '140',
        'liechtenstein': '141',
        'litauen': '142',
        'luxemburg': '143',
        'nordmazedonien': '144',
        'malta': '145',
        'moldau': '146',
        'monaco': '147',
        'niederlande': '148',
        'norwegen': '149',
        'kosovo': '150',
        'österreich': '151',
        'polen': '152',
        'portugal': '153',
        'rumänien': '154',
        'slowakei': '155',
        'san marino': '156',
        'schweden': '157',
        'schweiz': '158',
        'russische föderation': '160',
        'spanien': '161',
        'türkei': '163',
        'tschechien': '164',
        'ungarn': '165',
        'ukraine': '166',
        'vatikanstadt': '167',
        'vereinigtes königreich': '168',
        'weissrussland': '169',
        'serbien': '170',
        'zypern': '181',
        'gibraltar': '195',
        'übriges europa': '199',
        'algerien': '221',
        'angola': '223',
        'eritrea': '224',
        'äthiopien': '225',
        'lesotho': '226',
        'botsuana': '227',
        'benin': '229',
        'dschibuti': '230',
        'côte d\'ivoire': '231',
        'nigeria': '232',
        'simbabwe': '233',
        'gabun': '236',
        'gambia': '237',
        'ghana': '238',
        'mauretanien': '239',
        'cabo verde': '242',
        'kenia': '243',
        'komoren': '244',
        'kongo': '245',
        'kongo, demokratische republik': '246',
        'liberia': '247',
        'libyen': '248',
        'madagaskar': '249',
        'mali': '251',
        'marokko': '252',
        'mauritius': '253',
        'mosambik': '254',
        'niger': '255',
        'malawi': '256',
        'sambia': '257',
        'burkina faso': '258',
        'guinea-bissau': '259',
        'guinea': '261',
        'kamerun': '262',
        'südafrika': '263',
        'ruanda': '265',
        'namibia': '267',
        'são tomé und príncipe': '268',
        'senegal': '269',
        'seychellen': '271',
        'sierra leone': '272',
        'somalia': '273',
        'äquatorialguinea': '274',
        'sudan (vor der teilung des landes)': '276',
        'sudan': '277',
        'südsudan': '278',
        'eswatini': '281',
        'tansania': '282',
        'togo': '283',
        'tschad': '284',
        'tunesien': '285',
        'uganda': '286',
        'ägypten': '287',
        'zentralafrikanische republik': '289',
        'burundi': '291',
        'britisch abhängige gebiete in afrika': '295',
        'übriges afrika': '299',
        'antigua und barbuda': '320',
        'barbados': '322',
        'argentinien': '323',
        'bahamas': '324',
        'bolivien': '326',
        'brasilien': '327',
        'guyana': '328',
        'belize': '330',
        'chile': '332',
        'dominica': '333',
        'costa rica': '334',
        'dominikanische republik': '335',
        'ecuador': '336',
        'el salvador': '337',
        'grenada': '340',
        'guatemala': '345',
        'haiti': '346',
        'honduras': '347',
        'kanada': '348',
        'kolumbien': '349',
        'kuba': '351',
        'mexiko': '353',
        'nicaragua': '354',
        'jamaika': '355',
        'panama': '357',
        'paraguay': '359',
        'peru': '361',
        'suriname': '364',
        'uruguay': '365',
        'st. lucia': '366',
        'venezuela': '367',
        'vereinigte staaten': '368',
        'st. vincent und die grenadinen': '369',
        'st. kitts und nevis': '370',
        'trinidad und tobago': '371',
        'britisch abhängige gebiete in amerika': '395',
        'übriges amerika': '399',
        'hongkong': '411',
        'macau': '412',
        'jemen': '421',
        'armenien': '422',
        'afghanistan': '423',
        'bahrain': '424',
        'aserbaidschan': '425',
        'bhutan': '426',
        'myanmar': '427',
        'brunei darussalam': '429',
        'georgien': '430',
        'sri lanka': '431',
        'vietnam': '432',
        'korea, demokratische volksrepublik (nordkorea)': '434',
        'indien': '436',
        'indonesien': '437',
        'irak': '438',
        'iran': '439',
        'israel': '441',
        'japan': '442',
        'kasachstan': '444',
        'jordanien': '445',
        'kambodscha': '446',
        'katar': '447',
        'kuwait': '448',
        'laos': '449',
        'kirgisistan': '450',
        'libanon': '451',
        'malediven': '454',
        'oman': '456',
        'mongolei': '457',
        'nepal': '458',
        'palästinensische gebiete': '459',
        'bangladesch': '460',
        'pakistan': '461',
        'philippinen': '462',
        'taiwan': '465',
        'korea, republik (südkorea)': '467',
        'vereinigte arabische emirate': '469',
        'tadschikistan': '470',
        'turkmenistan': '471',
        'saudi-arabien': '472',
        'singapur': '474',
        'syrien': '475',
        'thailand': '476',
        'usbekistan': '477',
        'china': '479',
        'malaysia': '482',
        'übriges asien': '499',
        'australien': '523',
        'salomonen': '524',
        'nördliche marianen': '525',
        'fidschi': '526',
        'kiribati': '530',
        'nauru': '531',
        'vanuatu': '532',
        'neuseeland': '536',
        'palau': '537',
        'papua-neuguinea': '538',
        'tuvalu': '540',
        'tonga': '541',
        'samoa': '543',
        'marshallinseln': '544',
        'mikronesien': '545',
        'britisch abh. gebiete in australien/ozeanien': '595',
        'übriges ozeanien': '599',
        'unbekanntes ausland': '996',
        'staatenlos': '997',
        'ungeklärt': '998',
        'ohne angabe': '999',
        '': ''  # Default value
    }
    return country_mapping

def get_country_code_mapping():
    """Returns the mapping for nationality country codes (DIED 4213)"""
    country_codes = {
        'keine angabe': '0',
        'österreich': 'A',
        'afghanistan': 'AFG',
        'angola': 'AGO',
        'amerikanische jungferninseln': 'AJ',
        'albanien': 'AL',
        'andorra': 'AND',
        'anguilla': 'ANG',
        'antigua und barbuda': 'ANT',
        'antarktische territorien': 'AQ',
        'äquatorialguinea': 'AQU',
        'armenien': 'ARM',
        'amerikanisch samoa': 'AS',
        'aserbaidschan': 'ASE',
        'korallenmeer-, ashmore- und cartierinseln': 'AU',
        'australien': 'AUS',
        'aruba': 'AW',
        'åland': 'AX',
        'belgien': 'B',
        'bangladesch': 'BD',
        'barbados': 'BDS',
        'bermuda': 'BER',
        'bulgarien': 'BG',
        'belize': 'BH',
        'bhutan': 'BHT',
        'bosnien und herzegowina': 'BIH',
        'malediven': 'BIO',
        'britische jungferninseln': 'BJ',
        'st. barthélemy': 'BL',
        'bolivien': 'BOL',
        'bonaire, saba, st. eustatius': 'BQ',
        'brasilien': 'BR',
        'bahrain': 'BRN',
        'brunei darussalam': 'BRU',
        'bahamas': 'BS',
        'bouvetinsel': 'BV',
        'weissrussland': 'BY',
        'kuba': 'C',
        'kamerun': 'CAM',
        'kokosinseln': 'CC',
        'kanada': 'CDN',
        'schweiz': 'CH',
        'tschad': 'CHD',
        'côte d\'ivoire': 'CI',
        'sri lanka': 'CL',
        'kolumbien': 'CO',
        'cookinseln': 'COI',
        'clipperton': 'CP',
        'costa rica': 'CR',
        'cabo verde': 'CV',
        'curaçao': 'CW',
        'zypern': 'CY',
        'weihnachtsinsel': 'CX',
        'tschechien': 'CZ',
        'dänemark': 'DK',
        'dominikanische republik': 'DOM',
        'dschibuti': 'DSC',
        'benin': 'DY',
        'algerien': 'DZ',
        'spanien': 'E',
        'kenia': 'EAK',
        'tansania': 'EAT',
        'uganda': 'EAU',
        'ecuador': 'EC',
        'westsahara': 'EH',
        'eritrea': 'ERI',
        'el salvador': 'ES',
        'estland': 'EST',
        'ägypten': 'ET',
        'äthiopien': 'ETH',
        'frankreich': 'F',
        'falklandinseln': 'FAL',
        'französisch guayana': 'FG',
        'finnland': 'FIN',
        'fidschi': 'FJI',
        'liechtenstein': 'FL',
        'franz.-polynesien': 'FP',
        'färöer': 'FR',
        'gabun': 'GAB',
        'vereinigtes königreich': 'GB',
        'guatemala': 'GCA',
        'georgien': 'GEO',
        'guernsey': 'GG',
        'ghana': 'GH',
        'gibraltar': 'GIB',
        'griechenland': 'GR',
        'grönland': 'GRO',
        'südgeorgien und die südlichen sandwichinseln': 'GS',
        'guadeloupe': 'GUA',
        'guinea-bissau': 'GUB',
        'guam': 'GUM',
        'guyana': 'GUY',
        'ungarn': 'H',
        'honduras': 'HCA',
        'st. helena /ascension / tristan da cunha': 'HEL',
        'hongkong': 'HKG',
        'kroatien': 'HR',
        'heard und mcdonaldinseln': 'HM',
        'burkina faso': 'HV',
        'italien': 'I',
        'israel': 'IL',
        'indien': 'IND',
        'iran': 'IR',
        'irland': 'IRL',
        'irak': 'IRQ',
        'island': 'IS',
        'britisches territorium im indischen ozean': 'IO',
        'japan': 'J',
        'jamaika': 'JA',
        'jersey': 'JE',
        'jordanien': 'JOR',
        'kambodscha': 'K',
        'kaimaninseln': 'KAI',
        'kanalinseln': 'KAN',
        'kasachstan': 'KAS',
        'kiribati': 'KIB',
        'kirgisistan': 'KIS',
        'komoren': 'KOM',
        'korea, demokratische volksrepublik (nordkorea)': 'KOR',
        'kosovo': 'KOS',
        'kuwait': 'KWT',
        'luxemburg': 'L',
        'laos': 'LAO',
        'libyen': 'LAR',
        'liberia': 'LB',
        'lesotho': 'LS',
        'litauen': 'LT',
        'lettland': 'LV',
        'malta': 'M',
        'marokko': 'MA',
        'macau': 'MAC',
        'malaysia': 'MAL',
        'insel man': 'MAN',
        'oman': 'MAO',
        'marshallinseln': 'MAR',
        'martinique': 'MAT',
        'mayotte': 'MAY',
        'monaco': 'MC',
        'moldau': 'MD',
        'mexiko': 'MEX',
        'st. martin (französischer teil)': 'MF',
        'mikronesien': 'MIK',
        'nordmazedonien': 'MK',
        'montenegro': 'MNE',
        'mongolei': 'MON',
        'montserrat': 'MOT',
        'mosambik': 'MOZ',
        'mauritius': 'MS',
        'malawi': 'MW',
        'myanmar': 'MYA',
        'norwegen': 'N',
        'nauru': 'NAU',
        'nepal': 'NEP',
        'norfolkinseln': 'NF',
        'nicaragua': 'NIC',
        'niue': 'NIU',
        'neukaledonien': 'NKA',
        'niederlande': 'NL',
        'niederländische antillen': 'NLA',
        'nördliche marianen': 'NMA',
        'neuseeland': 'NZ',
        'portugal': 'P',
        'panama': 'PA',
        'palau': 'PAL',
        'peru': 'PE',
        'st. pierre und miquelon': 'PIE',
        'pitcairninseln': 'PIT',
        'pakistan': 'PK',
        'polen': 'PL',
        'papua-neuguinea': 'PNG',
        'puerto rico': 'PRI',
        'palästinensische gebiete': 'PSE',
        'paraguay': 'PY',
        'katar': 'QAT',
        'argentinien': 'RA',
        'botsuana': 'RB',
        'zentralafrikanische republik': 'RCA',
        'kongo': 'RCB',
        'chile': 'RCH',
        'réunion': 'REU',
        'guinea': 'RG',
        'haiti': 'RH',
        'indonesien': 'RI',
        'mauretanien': 'RIM',
        'libanon': 'RL',
        'madagaskar': 'RM',
        'mali': 'RMM',
        'niger': 'RN',
        'rumänien': 'RO',
        'korea, republik (südkorea)': 'ROK',
        'uruguay': 'ROU',
        'philippinen': 'RP',
        'san marino': 'RSM',
        'burundi': 'RU',
        'russische föderation': 'RUS',
        'ruanda': 'RWA',
        'schweden': 'S',
        'saudi-arabien': 'SAU',
        'serbien und montenegro': 'SCG',
        'st. kitts und nevis': 'SCN',
        'sudan': 'SDN',
        'singapur': 'SGP',
        'svalbard und jan mayen': 'SJ',
        'slowakei': 'SK',
        'slowenien': 'SLO',
        'suriname': 'SME',
        'senegal': 'SN',
        'salomonen': 'SOL',
        'somalia': 'SP',
        'serbien': 'SRB',
        'südsudan': 'SSD',
        'são tomé und príncipe': 'STP',
        'namibia': 'SWA',
        'eswatini': 'SWZ',
        'seychellen': 'SY',
        'syrien': 'SYR',
        'st. martin (niederländischer teil)': 'SX',
        'thailand': 'T',
        'tadschikistan': 'TAD',
        'französische süd- und antarktisgebiete': 'TF',
        'togo': 'TG',
        'china': 'TJ',
        'tunesien': 'TN',
        'tokelau': 'TOK',
        'tonga': 'TON',
        'türkei': 'TR',
        'trinidad und tobago': 'TT',
        'turks- und caicosinseln': 'TUC',
        'turkmenistan': 'TUR',
        'tuvalu': 'TUV',
        'taiwan': 'TWN',
        'ukraine': 'UA',
        'vereinigte arabische emirate': 'UAE',
        'navassa / kleinere amerikanische überseeinseln': 'UM',
        'vereinigte staaten': 'USA',
        'usbekistan': 'USB',
        'vatikanstadt': 'V',
        'vanuatu': 'VAN',
        'vietnam': 'VN',
        'gambia': 'WAG',
        'sierra leone': 'WAL',
        'nigeria': 'WAN',
        'dominica': 'WD',
        'wallis und futuna': 'WF',
        'grenada': 'WG',
        'st. lucia': 'WL',
        'samoa': 'WS',
        'st. vincent und die grenadinen': 'WV',
        'jemen': 'YEM',
        'jugoslawien': 'YU',
        'venezuela': 'YV',
        'sambia': 'Z',
        'südafrika': 'ZA',
        'kongo, demokratische republik': 'ZRE',
        'simbabwe': 'ZW',
        'deutschland': '0',  # Default to Germany
        '': '',
    }
    return country_codes
# DIED table mappings
DIED_MAPPINGS = {
    # DIED 4003: Gender
    "gender": {
        'male': '0',
        'female': '1',
        'transgender': '2',
        'non-conforming	': '2',
        'genderqueer': '2',
        'other': '2',
        'prefer not to say': '3',
        '': ''  # Default value
    },

    # DIED 4604: Highest education
    "custom_höchster_schulabschluss": {
        'keine angabe': '0',
        'ohne schulabschluss': '1',
        'haupt-/volksschulabschluss': '2',
        'mittlere reife oder gleichwertiger abschluss': '3',
        'abitur/fachabitur': '4',
        'abschluss unbekannt': '8',
        '': ''  # Default value
    },

    # DIED 4601: Professional education
    "custom_höchste_berufsausbildung": {
        'keine angabe': '0',
        'ohne beruflichen ausbildungsabschluss': '1',
        'abschluss einer anerkannten berufsausbildung': '2',
        'meister-/techniker - oder gleichwertiger fachschulabschluss': '3',
        'bachelor': '4',
        'diplom/magister/master/staatsexamen': '5',
        'promotion': '6',
        'abschluss unbekannt': '9',
        '': ''  # Default value
    },

    # DIED 4040: First employment
    "erstbeschaeftigung": {
        'nein': '0',
        'ja': '1',
        '': ''  # Default value
    },

    # DIED 440: Single parent / various yes/no fields
    "alleinerziehend": {
        'nein': '0',
        'ja': '1',
        '': ''  # Default value
    },

    # All yes/no fields with same mapping
    "arbeitszeit_18_std_mit_zulassung_aa": {
        'nein': '0',
        'ja': '1',
        '': ''
    },
    "arbeitsbescheinigung_im_austrittsmonat_elektr_ueberm": {
        'nein': '0',
        'ja': '1',
        '': ''
    },
    "automatische_loeschung_nach_austritt_unterdruecken": {
        'nein': '0',
        'ja': '1',
        '': ''
    },
    "bescheinigung_nach_313_sgb_iii_elektronisch_ueberm": {
        'nein': '0',
        'ja': '1',
        '': ''
    },
    "eel_meldung_nach_austritt_des_arbeitnehmers": {
        'nein': '0',
        'ja': '1',
        '': ''
    },
    "ehrenamtliche_taetigkeit": {
        'nein': '0',
        'ja': '1',
        '': ''
    },
    "einmalbezuege_nach_austritt_d_arbeitnehmers_berechnen": {
        'nein': '0',
        'ja': '1',
        '': ''
    },
    "ersteintrittsdatum_fuer_aag_und_brutto_netto_verwenden": {
        'nein': '0',
        'ja': '1',
        '': ''
    },
    "verheiratet": {
        'nein': '0',
        'ja': '1',
        '': ''
    },

    # DIED 4574: Employment relationship
    "custom_arbeitsverhältnis": {
        'unbefristet': '0',
        'befristet': '1',
        'zwechbefristet': '2',
        '': ''  # Default value
    },

    # DIED 4609: Remuneration form
    "entlohnungsform": {
        'stundenlohn': '0',
        'leistungslohn': '1',
        'gehalt': '2',
        '': ''  # Default to Gehalt
    },

    # DIED 4630: Main/secondary employer
    "kennzeichnung_arbeitgeber_haupt_nebenarbeitgeber": {
        'keine angabe': '0',
        'hauptarbeitgeber': '1',
        'nebenarbeitgeber': '2',
        '': ''  # Default value
    },

    # DIED 4624: Religious confession (Kirchensteuer)
    "konfessionszugehoerigkeit_steuerpflichtiger": {
        'konfessionslos / keine kirchensteuerberechnung': '0',
        'ev - evangelische kirchensteuer': '1',
        'rk - römisch-katholische kirchensteuer': '2',
        'ak - altkatholische kirchensteuer': '3',
        'fa - freie religionsgemeinschaft alzey': '4',
        'fb - freireligiöse landesgemeinde baden': '5',
        'fg - freireligiöse landesgemeinde pfalz': '6',
        'fm - freireligiöse gemeinde mainz': '7',
        'fr - französisch reformiert (bis 12/2015)': '8',
        'fs - freireligiöse gemeinde offenbach/main': '9',
        'ib - israelitische religionsgemeinschaft baden': '10',
        'ih - jüdische kultussteuer': '11',
        'il - israelitische kultussteuer der kultusberechtigten gemeinden': '12',
        'is - israelitische / jüdische kultussteuer': '13',
        'iw - israelitische religionsgemeinschaft württembergs': '14',
        'jd - jüdische kultussteuer': '15',
        'jh - jüdische kultussteuer': '16',
        'lt - evangelisch lutherisch (bis 12/2015)': '17',
        'rf - evangelisch reformiert (bis 12/2015)': '18',
        '': ''  # Default value
    },

    # DIED 4640: Disability status
    "custom_schwerbehinderung": {
        'nein': '0',
        '2 prozent': '1',
        '20 prozent': '2',
        '': ''  # Default value
    },

    # DIED 4214: Birth country - using same mapping as geburtsland in Personalerfassungsbogen
    "geburtsland": get_birth_country_mapping(),

    # DIED 4213: Nationality (country codes)
    "custom_land": get_country_code_mapping(),
    "staatsangehoerigkeit": get_country_code_mapping(),

    # DIED 1566: Tax class
    "steuerklasse_personaldaten_steuer_steuerkarte_allgemeine_daten": {
        '1': '1',
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '6': '6',
        '': ''  # Default to class 1
    },

    # DIED 460: Pauschalsteuer berechnen
    "pauschalsteuer_berechnen": {
        'nein': '0',
        '2 prozent': '1',
        '20 prozent': '2',
        '': ''  # Default value
    }
}


def format_date(date_str):
    """Format date to DD.MM.YYYY format."""
    if not date_str:
        return ""

    try:
        date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except:
        return date_str  # Return as is if not in expected format

def map_value_to_died(field_name, value):
    """Map a value from ERPNext to its DIED table equivalent."""
    # Skip mapping for empty values
    if value is None:
        return ""

    # Convert value to lowercase for case-insensitive mapping
    value_lower = str(value).lower() if value else ""

    # Handle special case for date fields
    if field_name in [
        "date_of_birth", "date_of_joining", "relieving_date",
        "arbeits_ausbildungsbeginn_tt_mm_jjjj", "arbeits_ausbildungsende_tt_mm_jjjj",
        "custom_befristung_arbeitserlaubnis", "custom_befristung_aufenthaltserlaubnis",
        "datum_des_todes", "custom_ersteintritt_ins_unternehmen_",
        "geburtsdatum_personaldaten_kinderdaten_allgemeine_angaben",
        "sb_ausweis_gueltig_ab_tt_mm_jjjj", "custom_befristung_gdb_bescheid",
        "tatsaechliches_ende_der_ausbildung", "voraussichtliches_ende_der_ausbildung_gem_vertrag",
        "studienbescheinigung", "beginn_der_ausbildung"
    ]:
        return format_date(value)

    # Handle numeric fields that don't need mapping (passthrough)
    if field_name in [
         "jobticket_hoehe_des_geldwerten_vorteils",
        "basislohn", "stundenlohn", "stundenlohn_1",
        "anzahl_kinderfreibeträge",
        "grundurlaubsanspruch", "urlaubsanspruch_aktuelles_jahr",
        "custom_summe_wochenarbeitszeit", "kind_nummer"
    ]:
        return value

    # Handle string fields that don't need mapping (passthrough)
    if field_name in [
        "last_name", "first_name", "personal_email", "cell_number",
        "custom_straße", "custom_hausnummer", "custom_ort", "custom_plz",
        "iban", "bic", "geburtsname", "geburtsort", "versicherungsnummer",
        "ausweis_nr_aktenzeichen", "employee_number", "namenszusatz_geburtsname",
        "namenszusatz_mitarbeitername", "vorsatzwort_geburtsname", "vorsatzwort_mitarbeitername",
        "familienname_personaldaten_kinderdaten_allgemeine_angaben",
        "vorname_personaldaten_kinderdaten_allgemeine_angaben",
        "ausstellende_dienststelle", "abweichender_kontoinhaber", "abteilung_datev_lodas" ,"akademischer_grad",
        "custom_anschriftenzusatz", "ort_der_dienststelle"
    ]:
        return value

    # Check if field has a mapping
    if field_name in DIED_MAPPINGS:
        mapping = DIED_MAPPINGS[field_name]

        # Try to get mapped value using lowercase for case-insensitive matching
        result = mapping.get(value_lower, "")

        # If no mapping found, log an error and use default
        if not result and value_lower:
            frappe.log_error(
                f"Value '{value}' for field '{field_name}' has no DIED mapping",
                "DATEV Export Error"
            )
            result = mapping.get('', "")  # Get default value
            if not result:
                result = value  # If no default, use original value
    else:
        # For fields without specific mappings, return the original value
        result = value

    return result