import re
from .tafdecoder import Decoder

"""overload dei metodi di decodifica del TAF per traduzione in lingua italiana, estende la libreria pytaf"""
class Decoder_it(Decoder):
    def __init__(self, taf):
        super().__init__(taf)

    def decode_taf(self):
        form = self._taf.get_header()["form"]
        result = ""

        result += self._decode_header(self._taf.get_header()) + "\n"

        for group in self._taf.get_groups():
            # TAF specific stuff
            if form == "taf":
                if group["header"]:
                    result += self._decode_group_header(group["header"]) + "\n"

            # METAR specific stuff
            if form == "metar":
                if group["temperature"]:
                    result += "    Temperatura %s\n" % self._decode_temperature(group["temperature"])

                if group["pressure"]:
                    result += "    Pressione %s\n" % self._decode_pressure(group["pressure"])

            # Both TAF and METAR
            if group["wind"]:
                result += "    Vento %s \n" % self._decode_wind(group["wind"])

            if group["visibility"]:
                result += "    Visibilità %s \n" % self._decode_visibility(group["visibility"])

            if group["clouds"]:
                result += "    Cielo %s \n" % self._decode_clouds(group["clouds"])

            if group["weather"]:
                result += "    Meteo %s \n" % self._decode_weather(group["weather"])

            if group["windshear"]:
                result += "    Wind Shear %s\n" % self._decode_windshear(group["windshear"])

            result += " \n"

        if self._taf.get_maintenance():
            result += self._decode_maintenance(self._taf.get_maintenance())

        return(result)    

    def _decode_header(self, header):
        result = ""

        # Ensure it's side effect free
        _header = header

        if _header["form"] == 'taf':
            # Decode TAF header
            # Type
            if _header["type"] == "AMD":
                result += "TAF emendato per "
            elif _header["type"] == "COR":
                result += "TAF corretto per "
            elif _header["type"] == "RTD":
               result += "TAF relativo a "
            else:
                result += "TAF per "

            _header["origin_date"] = _header["origin_date"].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
            _header["valid_from_date"] = _header["valid_from_date"].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
            _header["valid_till_date" ] = _header["valid_till_date"].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")


            result += ("%(icao_code)s emesso alle %(origin_hours)s:%(origin_minutes)s UTC giorno %(origin_date)s, " 
                       "valido dalle %(valid_from_hours)s:00 UTC del %(valid_from_date)s fino alle %(valid_till_hours)s:00 UTC del %(valid_till_date)s")
        else:
            # Decode METAR header
            # Type
            if _header["type"] == "COR":
                result += "METAR corretto per "
            else:
                result += "METAR per "

            _header["origin_date"] = _header["origin_date"].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")

            result += ("%(icao_code)s emesso alle %(origin_hours)s:%(origin_minutes)s UTC giorno %(origin_date)s")

        result = result % _header

        return(result)
    
    def _decode_group_header(self, header):
        result = ""
        _header = header

        _header["from_date"] = _header["from_date"].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
        _header["till_date" ] = _header["till_date"].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")


        from_str = "Dalle %(from_hours)s:%(from_minutes)s il %(from_date)s: "
        prob_str = "Probabilità %(probability)s%% tra le %(from_hours)s:00 del %(from_date)s e le %(till_hours)s:00 del %(till_date)s: "
        tempo_str = "Cambiamento temporaneo fra le %(from_hours)s:00 del %(from_date)s e le %(till_hours)s:00 del %(till_date)s dei fenomeni: "
        prob_tempo_str = "Probabilità %(probability)s%% di cambiamento temporaneo tra le %(from_hours)s:00 del %(from_date)s e le %(till_hours)s:00 del %(till_date)s dei fenomeni: "
        becmg_str = "Cambio graduale tra le %(from_hours)s:00 del %(from_date)s e le %(till_hours)s:00 del %(till_date)s dei fenomeni: "

        if "type" in _header:

            if _header["type"] == "FM":
                result += from_str % { "from_date":    _header["from_date"],
                                       "from_hours":   _header["from_hours"],
                                       "from_minutes": _header["from_minutes"] }
            elif _header["type"] == "PROB%s" % (_header["probability"]):
                result += prob_str % { "probability": _header["probability"],
                                       "from_date":   _header["from_date"],
                                       "from_hours":  _header["from_hours"],
                                       "till_date":   _header["till_date"],
                                       "till_hours":  _header["till_hours"] }
            elif "PROB" in _header["type"] and "TEMPO" in _header["type"]:
                result += prob_tempo_str % { "probability": _header["probability"],
                                           "from_date":   _header["from_date"],
                                           "from_hours":  _header["from_hours"],
                                           "till_date":   _header["till_date"],
                                           "till_hours":  _header["till_hours"] }
            elif _header["type"] == "TEMPO":
                result += tempo_str % { "from_date":  _header["from_date"],
                                        "from_hours": _header["from_hours"],
                                        "till_date":  _header["till_date"],
                                        "till_hours": _header["till_hours"] }
            elif _header["type"] == "BECMG":
                result += becmg_str % { "from_date":  _header["from_date"],
                                        "from_hours": _header["from_hours"],
                                        "till_date":  _header["till_date"],
                                        "till_hours": _header["till_hours"] }

        return(result)

    def _decode_wind(self, wind):
        unit = ""
        result = ""

        if wind["direction"] == "000":
            return("calmo")
        elif wind["direction"] == "VRB":
            result += "Variabile"
        else:
            result += "da %s gradi" % wind["direction"]

        if wind["unit"] == "KT":
            unit = "nodi"
        elif wind["unit"] == "MPS":
            unit = "metri al secondo"
        else:
            # Unlikely, but who knows
            unit = "(unità sconosciuta)"

        result += " a %s %s" % (wind["speed"], unit)

        if wind["gust"]:
            result += " raffiche da %s %s" % (wind["gust"], unit)

        return(result)

    def _decode_visibility(self, visibility):
        result = ""

        if "more" in visibility:
            if visibility["more"]:
                result += "più di "

        result += visibility["range"]

        if visibility["unit"] == "SM":
            result += " miglia terrestri"
        elif visibility["unit"] == "M":
            result += " metri"

        return(result)

    def _decode_clouds(self, clouds):
        result = ""
        i_result = ""
        list = []

        for layer in clouds:
            if layer["layer"] == "SKC" or layer["layer"] == "CLR":
                return "limpido"

            if layer["layer"] == "NSC":
                return "senza nuvole significative"

            if layer["layer"] == "CAVOK":
                return "senza fenomeni significativi"

            if layer["layer"] == "CAVU":
                return "copertura e visibilità senza restrizioni"
            
            if layer["layer"] == "VV///":
                return "oscurato"

            if layer["layer"] == "SCT":
                layer_type = "nubi sparse"
            elif layer["layer"] == "BKN":
                layer_type = "molto nuvoloso"
            elif layer["layer"] == "FEW":
                layer_type = "poche nubi"
            elif layer["layer"] == "OVC":
                layer_type = "coperto"

            if layer["type"] == "CB":
                type = "cumulonembo"
            elif layer["type"] == "CU":
                type = "cumulo"
            elif layer["type"] == "TCU":
                type = "cumulo torreggiante"
            elif layer["type"] == "CI":
                type = "cirro"
            else:
                type = ""

            result = "%s %s a %d piedi" % (layer_type, type, int(layer["ceiling"])*100)

            # Remove extra whitespace, if any
            result = re.sub(r'\s+', ' ', result)

            list.append(result)

            layer = ""
            type = ""
            result = ""

        result = ", ".join(list)
        return(result)

    def _decode_weather(self, weather):
        # Dicts for translating the abbreviations
        dict_intensities = {
            "-" : "leggera",
            "+" : "forte",
            "VC" : "nelle vicinanze",
            "RE" : "recente"
        }

        dict_modifiers = {
            "MI" : "debole",
            "BC" : "irregolare",
            "DR" : "bassa deriva",
            "BL" : "soffiante",
            "SH" : "scroscio",
            "TS" : "temporale",
            "FZ" : "congelante",
            "PR" : "parziale"
        }

        dict_phenomenons = {
            "DZ" : "pioviggine",
            "RA" : "pioggia",
            "SN" : "neve",
            "SG" : "granelli di neve",
            "IC" : "ghiaccio",
            "PL" : "pellet di ghiaccio",
            "GR" : "grandine",
            "GS" : "neve/pellet di ghiaccio",
            "UP" : "precipitatione sconosciuta",
            "BR" : "foschia",
            "FG" : "nebbia",
            "FU" : "fumo",
            "DU" : "polvere",
            "SA" : "sabbia",
            "HZ" : "caligine",
            "PY" : "getti",
            "VA" : "ceneri vulcaniche",
            "PO" : "vortici di polvere/sabbia",
            "SQ" : "burrasca",
            "FC" : "nuvola a imbuto",
            "SS" : "tempesta di sabbia",
            "DS" : "tempesta di polvere",
        }

        weather_txt_blocks = []

        # Check for special cases first. If a certain combination is found
        # then skip parsing the whole weather string and return a defined string
        # immediately
        for group in weather:
            # +FC = Tornado or Waterspout
            if "+" in group["intensity"] and "FC" in group["phenomenon"]:
                weather_txt_blocks.append("tornado o tromba marina")
                continue

            # Sort the elements of the weather string, if no special combi-
            # nation is found.
            intensities_pre = []
            intensities_post = []
            if "RE" in group["intensity"]:
                intensities_pre.append("RE")
                group["intensity"].remove("RE")
            for intensity in group["intensity"]:
                if intensity != "VC":
                    intensities_pre.append(intensity)
                else:
                    intensities_post.append(intensity)

            modifiers_pre = []
            modifiers_post = []
            for modifier in group["modifier"]:
                if modifier != "TS" and modifier != "SH":
                    modifiers_pre.append(modifier)
                else:
                    modifiers_post.append(modifier)

            phenomenons_pre = []
            phenomenons_post = []
            for phenomenon in group["phenomenon"]:
                if phenomenon != "UP":
                    phenomenons_pre.append(phenomenon)
                else:
                    phenomenons_post.append(phenomenon)

            # Build the human readable text from the single weather string
            # and append it to a list containing all the interpreted text
            # blocks from a TAF group
            weather_txt = ""
            for intensity in intensities_pre:
                weather_txt += dict_intensities[intensity] + " "

            for modifier in modifiers_pre:
                weather_txt += dict_modifiers[modifier] + " "

            phenomenons = phenomenons_pre + phenomenons_post
            cnt = len(phenomenons)
            for phenomenon in phenomenons:
                weather_txt = dict_phenomenons[phenomenon] + " " + weather_txt
                if cnt > 2:
                    weather_txt += ", "
                if cnt == 2:
                    weather_txt += " e "
                cnt = cnt-1
            weather_txt += " "

            for modifier in modifiers_post:
                weather_txt += dict_modifiers[modifier] + " "

            for intensity in intensities_post:
                weather_txt += dict_intensities[intensity] + " "

            weather_txt_blocks.append(weather_txt.strip())

        # Put all the human readable stuff together and return the final
        # output as a string.
        weather_txt_full = ""
        for block in weather_txt_blocks[:-1]:
            weather_txt_full += block + " / "
        weather_txt_full += weather_txt_blocks[-1]

        return(weather_txt_full)

    def _decode_temperature(self, temperature, unit='C'):
        if temperature["air_prefix"] == 'M':
            air_c = int(temperature["air"])*-1
        else:
            air_c = int(temperature["air"])

        if temperature["dewpoint_prefix"] == 'M':
            dew_c = int(temperature["dewpoint"])*-1
        else:
            dew_c = int(temperature["dewpoint"])

        if unit == 'C':
            air_txt = air_c
            dew_txt = dew_c

        if unit == 'F':
            air_f = int(round(air_c*1.8+32))
            dew_f = int(round(dew_c*1.8+32))
            air_txt = air_f
            dew_txt = dew_f

        result = "aria %s°%s <br/> Punto di rugiada %s°%s" % (air_txt, unit, dew_txt, unit)
        return(result)

    def _decode_pressure(self, pressure):
        result = "%s hPa" % (pressure["athm_pressure"])
        return(result)

    def _decode_windshear(self, windshear):
        result = "a %s, venti %s a %s %s" % ((int(windshear["altitude"])*100), windshear["direction"], windshear["speed"], windshear["unit"])
        return(result)

    def _decode_maintenance(self, maintenance):
        if maintenance:
            return "Stazione in manutenzione\n"
