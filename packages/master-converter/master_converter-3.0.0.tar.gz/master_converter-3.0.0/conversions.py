
class Length:
    class Millimeters:
    
        def __init__(self, mm):
            """
            A class for common millimeter conversions
            :int mm: The number of millimeters converted
            """
            if type(mm) is str:
                raise TypeError(f"mi can only be int or float, not {type(mm)}")
            else:
                self.mm = mm
    
        def Millimeters_Centimeters(self):
            """
            Converts millimeters to centimeters
            """
    
            cm = self.mm / 10
            return cm
    
        def Millimeters_Meters(self):
            """
            Converts millimeters to centimeters
            """
    
            m = self.mm / 1000
            return m
    
        def Millimeters_Inches(self):
            """
            Converts millimeters to inches
            """
    
            i = self.mm / 25.4
            return i
    
        def Millimeters_Kilometers(self):
            """
            Converts millimeters to kilometers and returns the number of kilometers
            """
    
            km = self.mm / 1000000
            return km
    
        def Millimeters_Feet(self):
            """
            Converts millimeters to feet and returns the number of feet
            """
    
            ft = self.mm / 304.8
            return ft
    
        def Millimeters_Yards(self):
            """
            Converts millimeters to yards and returns the number of yards
            """
    
            yd = self.mm / 914.4
            return yd
    
        def Millimeters_Miles(self):
            """
            Converts millimeters to miles and returns the number of miles
            """
    
            mi = self.mm / 1609344
            return mi
    
        def Millimeters_Nautical_Miles(self):
            """
            Converts millimeters to nautical miles and returns the number of nautical miles
            """
    
            nmi = self.mm / 1852000
            return nmi
    class Centimeters:
        def __init__(self, cm):
            """
            A class for common centimeter conversions
            :int cm: The number of centimeters you want converted
            """
            if type(cm) is str:
                raise TypeError(f"mi can only be int or float, not {type(cm)}")
            else:
                self.cm = cm
        def Centimeters_Millimeters(self):
            """
            Converts Centimeters to Millimeters and returns the number of Millimeters
            """
    
            mm = self.cm * 10
            return mm
    
        def Centimeters_Meters(self):
                """
                Converts Centimeters to Millimeters and returns the number of Millimeters
                """
    
                m = self.cm / 100
                return m
    
        def Centimeters_Inches(self):
                """
                Converts Centimeters to Inches and returns the number of Inches
                """
    
                i = self.cm / 2.54
                return i
    
        def Centimeters_Kilometers(self):
            """
            Converts centimeters to kilometers and returns the number of feet
            """
    
            km = self.cm / 100000
            return km
    
        def Centimeters_Feet(self):
            """
            Converts centimeters to feet and returns the number of feet
            """
    
            ft = self.cm / 30.48
            return ft
    
        def Centimeters_Yards(self):
            """
            Converts centimeters to yards and returns the number of yards
            """
    
            yd = self.cm / 91.44
            return yd
    
        def Centimeters_Miles(self):
            """
            Converts centimeters to miles and returns the number of miles
            """
    
            mi = self.cm / 160934.4
            return mi
    
        def Centimeters_Nautical_Miles(self):
            """
            Converts centimeters to nautical miles and returns the number of nautical miles
            """
    
            nmi = self.cm / 185200
            return nmi
    class Meters:
        def __init__(self, m):
            """
            A class for common meter conversions
            :int m:
            """
            if type(m) is str:
                raise TypeError(f"mi can only be int or float, not {type(m)}")
            else:
                self.m = m
    
        def Meters_Millimeters(self):
            """
            Converts Meters to Millimeters
            """
            mm = self.m * 1000
            return mm
    
        def Meters_Centimeters(self):
                """
                Converts Meters to Centimeters
                """
                cm = self.m * 100
                return cm
    
        def Meters_Yards(self):
                """
                Converts Meters to Yards
                """
                y = self.m / 0.9144
                return y
    
        def Meters_Kilometers(self):
            """
            Converts meters to kilometers and returns the number of kilometers
            """
    
            km = self.m / 1000
            return km
    
        def Meters_Inches(self):
            """
            Converts meters to inches nd returns the number of inches
            """
    
            inches = self.m / 0.0254
            return inches
    
        def Meters_Feet(self):
            """
            Converts meters to feet and returns the number of feet
            """
    
            ft = self.m / 0.3048
            return ft
    
        def Meters_Miles(self):
            """
            Converts meters to miles and returns the number of miles
            """
    
            mi = self.m / 1609.344
            return mi
    
        def Meters_Nautical_Miles(self):
            """
            Converts meters to nautical miles
            """
    
            nmi = self.m / 1852
            return nmi
    class Kilometers:
        def __init__(self, km):
            """
            A class for common kilometer conversions
            :int km: The number of kilometers you want converted
            """
    
            if type(km) is str:
                raise TypeError(f"mi can only be int or float, not {type(km)}")
            else:
                self.km = km
    
        def Kilometers_Millimeters(self):
            """
            Converts kilometers to millimeters and returns the number of millimeters
            """
    
            mm = self.km * 1000000
            return mm
    
        def Kilometers_Centimeters(self):
            """
            Converts kilometers to centimeters and returns the number of centimeters
            """
    
            cm = self.km * 100000
            return cm
    
        def Kilometers_Meters(self):
            """
            Converts kilometers to meters and returns the number of meters
            """
            m = self.km * 1000
            return m
    
        def Kilometers_Inches(self):
            """
            Converts kilometers to inches and returns the number of inches
            """
    
            inches = self.km / 0.0000254
            return inches
    
        def Kilometers_Feet(self):
            """
            Converts kilometers to feet and returns the number of feet
            """
    
            ft = self.km / 0.0003048
            return ft
    
        def Kilometers_Yards(self):
            """
            Converts kilometers to yards and returns the number of yards
            """
    
            yd = self.km / 0.0009144
            return yd
    
        def Kilometers_Miles(self):
            """
            Converts kilometers to meters and returns the number of miles
            """
    
            m = self.km / 1.609344
            return m
    
        def Kilometers_Nautical_Miles(self):
            """
            Converts kilometers to nautical miles
            """
    
            nmi = self.km / 1.852
            return nmi
    class Inches:
        def __init__(self, inches):
            """
            A class for common kilometer conversions
            :int inches: The number of inches you want converted
            """
    
            if type(inches) is str:
                raise TypeError(f"mi can only be int or float, not {type(str)}")
            else:
                self.inches = inches
    
        def Inches_Millimeters(self):
            """
            Converts Inches to Millimeters and returns the number of Millimeters
            """
    
            mm = self.inches * 25.4
            return mm
    
        def Inches_Centimeters(self):
            """
            Converts inches to centimeters and returns the number of centimeters
            """
    
            cm = self.inches * 2.54
            return cm
    
        def Inches_Meters(self):
            """
            Converts inches to meters and returns the number of meters
            """
    
            m = self.inches * 0.0254
            return m
    
        def Inches_Kilometers(self):
            """
            Converts inches to kilometers and returns the number of kilometers
            """
    
            km = self.inches * 0.0000254
            return km
    
        def Inches_Feet(self):
            """
            Converts inches to feet and returns the number of feet
            """
    
            ft = self.inches / 12
            return ft
    
        def Inches_Yards(self):
            """
            Converts inches to yards and returns the number of yards
            """
    
            yd = self.inches / 36
            return yd
    
        def Inches_Miles(self):
            """
            Converts inches to miles and returns the numer of miles
            """
    
            mi = self.inches / 63360
            return mi
    
        def Inches_Nautical_Miles(self):
            """
            Converts inches to nautical miles and returns the number of nautical miles
            """
    
            nmi = self.inches / 72913.3858
            return nmi
    class Feet:
        def __init__(self, ft):
            """
            A class for common feet conversions
            :int ft: The number of feet you want converted
            """
            if type(ft) is str:
                raise TypeError(f"mi can only be int or float, not {type(ft)}")
            else:
                self.ft = ft
    
        def Feet_Millimeters(self):
            """
            Converts feet to millimeters and returns the number of millimeters
            """
    
            mm = self.ft * 304.8
            return mm
    
        def Feet_Centimeters(self):
            """
            Converts feet to centimeters and returns the number of centimeters
            """
    
            ft = self.ft * 30.48
            return ft
    
        def Feet_Meters(self):
            """
            Converts feet to meters and returns the number of meters
            """
    
            m = self.ft * 0.3048
            return m
    
        def Feet_Kilometers(self):
            """
            Converts feet to kilometers and returns the number of kilometers
            """
    
            km = self.ft * 0.0003048
            return km
    
        def Feet_Inches(self):
            """
            Converts feet to inches and returns the number of inches
            """
    
            inches = self.ft * 12
            return inches
    
        def Feet_Yards(self):
            """
            Converts feet to yards and returns the number of yards
            """
    
            yd = self.ft / 3
            return yd
    
        def Feet_Miles(self):
            """
            Converts feet to miles and returns the number of miles
            """
    
            mi = self.ft / 5280
            return mi
    
        def Feet_Nautical_Miles(self):
            """
            Converts feet to nautical miles and returns the number of nautical miles
            """
    
            nmi = self.ft / 6076.11549
            return nmi
    class Yards:
        def __init__(self, yd):
            """
            A class for common yard conversions
            :int yd: The number of yards you want converted
            """
            if type(yd) is str:
                raise TypeError(f"mi can only be int or float, not {type(yd)}")
            else:
                self.yd = yd
    
        def Yards_Millimeters(self):
            """
            Converts yards to millimeters and returns the number millimeters
            """
    
            mm = self.yd * 914.4
            return mm
    
        def Yards_Centimeters(self):
            """
            Converts yards to centimeters and returns the number of centimeters
            """
    
            cm = self.yd * 91.44
            return cm
    
        def Yards_Meters(self):
            """
            Converts yards to meters and returns the number of meters
            """
    
            m = self.yd * 0.9144
            return m
    
        def Yards_Kilometers(self):
            """
            Converts yards to meters
            """
    
            km = self.yd * 0.0009144
            return km
    
        def Yards_Inches(self):
            """
            Converts Yards to Inches
            """
    
            inches = self.yd * 36
            return inches
    
        def Yards_Feet(self):
            """
            Converts yards to feet and returns the number of feet
            """
    
            ft = self.yd * 3
            return ft
    
        def Yards_Miles(self):
            """
            Converts yards to miles and returns the number of miles
            """
    
            mi = self.yd / 1760
            return mi
    
        def Yards_Nautical_Miles(self):
            """
            Converts yards to nautical miles and returns the number of nautical miles
            """
    
            nmi = self.yd / 2025.37183
            return nmi
    class Miles:
        def __init__(self, mi):
            """
            A class for common mile conversions
            :int mi: The number of miles you want converted
            """
    
            if type(mi) is str:
                raise TypeError(f"mi can only be int or float, not {type(mi)}")
            else:
                self.mi = mi
    
        def Miles_Millimeters(self):
            """
            Converts miles to millimeters and returns the number of millimeters
            """
    
            mm = self.mi * 1609344
            return mm
    
        def Miles_Centimeters(self):
            """
            Converts miles to centimeters and returns the number of centimeters
            """
    
            cm = self.mi * 160934.4
            return cm
    
        def Miles_Meters(self):
            """
            Converts miles to meters and returns the number of meters
            """
    
            m = self.mi * 1609.344
            return m
    
        def Miles_Kilometers(self):
            """
            Converts miles to kilometers and returns the number of kilometers
            """
    
            km = self.mi * 1.609344
            return km
    
        def Miles_Inches(self):
            """
            Converts miles to inches and returns the number of inches
            """
    
            inches = self.mi * 63360
            return inches
    
        def Miles_Feet(self):
            """
            Converts miles to feet and returns the number of feet
            """
    
            ft = self.mi * 5280
            return ft
    
        def Miles_Yards(self):
            """
            Converts miles to yards and returns the number of yards
            """
    
            yd = self.mi * 1760
            return yd
    
        def Miles_Nautical_Miles(self):
            """
            Converts miles to nautical miles and returns the number of nautical miles
            """
    
            nmi = self.mi / 1.15078
            return nmi
    class Nautical_Miles:
        def __init__(self, nmi):
            """
            A class for common Nautical Mile conversions
            :int nmi: The number of Nautical Miles you want converted
            """
    
            if type(nmi) is str:
                raise TypeError(f"mi can only be int or float, not {type(nmi)}")
            else:
                self.nmi = nmi
    
        def Nautical_Miles_Millimeters(self):
            """
            Converts nautical miles to millimeters and returns the number of millimeters
            """
    
            mm = self.nmi * 1852000
            return mm
    
        def Nautical_Miles_Centimeters(self):
            """
            Converts nautical miles to centimeters and returns the number of meters
            """
    
            cm = self.nmi * 185200
            return cm
    
        def Nautical_Miles_Meters(self):
            """
            Converts nautical miles to meters and returns the number of meters
            """
    
            m = self.nmi * 1852
            return m
    
        def Nautical_Miles_Kilometers(self):
            """
            Converts nautical miles to kilometers and returns the number of kilometers
            """
    
            km = self.nmi * 1.852
            return km
    
        def Nautical_Miles_Inches(self):
            """
            Converts nautical miles to inches and returns the number of inches
            """
    
            inches = self.nmi * 72913.3858
            return inches
    
        def Nautical_Miles_Feet(self):
            """
            Converts nautical miles to feet
            """
    
            ft = self.nmi * 6076.11549
            return ft
    
        def Nautical_Miles_Yards(self):
            """
            Converts nautical miles to yards and returns the number of yards
            """
    
            yd = self.nmi * 2025.37183
            return yd
    
        def Nautical_Miles_Miles(self):
            """
            Converts nautical miles to miles and returns the number of miles
            """
    
            m = self.nmi * 1.15078
            return m

class Mass:
    class Grams:
        def __init__(self, g):
            if type(g) is str:
                raise TypeError(f"mi can only be int or float, not {type(g)}")
            else:
                self.g = g

        def Grams_Milligrams(self):
            """
            Converts grams to milligrams and returns the number of milligrams
            """

            mg = self.g * 1000
            return mg

        def Grams_Kilograms(self):
            """
            Converts grams to kilograms and returns the number of milligrams
            """

            kg = self.g / 1000
            return kg

        def Grams_Ounces(self):
            """
            Converts grams to ounces and returns the number of ounces
            """

            oz = self.g / 28.3495231
            return oz

        def Grams_Pounds(self):
            """
            Converts grams to pounds and returns the number of pounds
            """

            lb = self.g / 453.59237
            return lb

        def Grams_Metric_Tons(self):
            """Converts grams to metric tons and returns the number of metric tons"""

            tonnes = self.g / 1000000
            return tonnes

        def Grams_Short_Tons(self):
            """Converts grams to short tons (Also known as US tons) and returns the number of short tons"""

            tonnes = self.g / 907184.74
            return tonnes

        def Grams_Long_Tons(self):
            """Converts grams to long tons (Also known as the Imperial Ton) and returns the number of long tons"""

            lt = self.g / 1016046.91
            return lt

    class Kilograms:
        def __init__(self, kg):

            if type(kg) is str:
                raise TypeError(f"mi can only be int or float, not {type(kg)}")
            else:
                self.kg = kg

        def Kilograms_Grams(self):
            """
            Converts kilograms to grams and returns the number of grams
            """

            g = self.kg * 1000
            return g

        def Kilograms_Milligrams(self):
            """
            Converts kilograms to milligrams and returns the number of milligrams
            """

            mg = self.kg * 1000000
            return mg

        def Kilograms_Pounds(self):
            """
            Converts kilograms to pounds and returns the number of pounds
            """

            lb = self.kg / 0.45359237
            return lb

        def Kilograms_Ounces(self):
            """
            Converts kilograms to ounces and returns the number of ounces
            """

            oz = self.kg / 0.0283495231
            return oz

        def Kilograms_Metric_Tons(self):
            """
            Converts kilograms to metric tons and returns the number of metric tons
            """

            tonnes = self.kg / 1000
            return tonnes

        def Kilograms_Short_Tons(self):
            """Converts kilograms to short tons (or US Ton) and returns the number of short tons"""

            st = self.kg / 907.18474
            return st

        def Kilograms_Long_Tons(self):
            """Converts kilograms to long tons (Also known as Imperial Tons) and returns the number of long tons"""

            lt = self.kg / 1016.04691
            return lt

    class Milligrams:
        def __init__(self, mg):
            if type(mg) is str:
                raise TypeError(f"mi can only be int or float, not {type(mg)}")
            else:
                self.mg = mg

        def Milligrams_Grams(self):
            """
            Converts milligrams to grams
            """

            g = self.mg / 1000
            return g

        def Milligrams_Kilograms(self):
            """
            Converts milligrams to kilograms and returns the number of kilograms
            """

            kg = self.mg / 1000000
            return kg

        def Milligrams_Pounds(self):
            """
            Converts milligrams to pounds and returns the number of pounds
            """

            lb = self.mg / 453592.37
            return lb

        def Milligrams_Ounces(self):
            """Converts milligrams to ounces and returns the number of ounces"""

            oz = self.mg / 28349.5231
            return oz

        def Milligrams_Metric_Tons(self):
            """Converts milligrams to metric tons and returns the number of metric tons"""

            tonnes = self.mg / 1000000000
            return tonnes

        def Milligrams_Short_Tons(self):
            """Converts milligrams to short tons (Also known as US tons) and returns the number of short tons"""

            st = self.mg / 907184740
            return st

        def Milligrams_Long_Tons(self):
            """Converts milligrams to long tons (or Imperial Tons) and returns the number of long tons"""

            lt = self.mg / 1016046909
            return lt

    class Pounds:
        def __init__(self, lb):
            if type(lb) is str:
                raise TypeError(f"mi can only be int or float, not {type(lb)}")
            else:
                self.lb = lb

        def Pounds_Ounces(self):
            """
            Converts pounds to ounces and returns the number of ounces
            """

            oz = self.lb * 16
            return oz

        def Pounds_Grams(self):
            """
            Converts pounds to grams and returns the number of grams
            """

            g = self.lb * 453.59237
            return g

        def Pounds_kilograms(self):
            """
            Converts pounds to kilograms and returns the number of kilograms
            """

            kg = self.lb * 0.45359237
            return kg

        def Pounds_Milligrams(self):
            """
            Converts pounds to milligrams and returns the number of milligrams
            """

            mg = self.lb * 453592.37
            return mg

        def Pounds_Metric_Tons(self):
            """Converts pounds to metric tons and returns the number of metric tons"""

            mt = self.lb * 0.00045359237
            return mt

        def Pounds_Short_Tons(self):
            """Converts pounds short tons (Also known as US Tons) and returns the number of short tons"""

            st = self.lb / 2000
            return st

        def Pounds_Long_Tons(self):
            """Converts pounds to long tons (Also known as Imperial Tons) and returns the number of long tons"""

            lt = self.lb / 2240
            return lt

    class Ounces:
        def __init__(self, oz):
            if type(oz) is str:
                raise TypeError(f"mi can only be int or float, not {type(oz)}")
            else:
                self.oz = oz

        def Ounces_Grams(self):
            """
            Converts ounces to grams and returns the number pf grams
            """

            g = self.oz * 28.3495231
            return g

        def Ounces_Kilograms(self):
            """
            Converts ounces to kilograms and returns the number of kilograms
            """

            kg = self.oz * 0.0283495231
            return kg

        def Ounces_Milligrams(self):
            """
            Converts ounces to milligrams and returns the number of milligrams
            """

            mg = self.oz * 28349.5231
            return mg

        def Ounces_Pounds(self):
            """
            Converts ounces to pounds and returns the number of pounds
            """

            lb = self.oz / 16
            return lb

        def Ounces_Metric_Tons(self):
            """Converts ounces to metric tons"""

            tonnes = self.oz * 0.0000283495231
            return tonnes

        def Ounces_Short_Tons(self):
            """Converts ounces to short tons (Also known as US Tons) and returns the number of short tons"""

            st = self.oz / 32000
            return st

        def Ounces_Long_Tons(self):
            """Converts ounces to long tons (Also known as Imperial Tons) and returns the number of long tons"""

            lt = self.oz / 35840
            return lt

    class Metric_Tons:
        def __init__(self, tonne):
            if type(tonne) is str:
                raise TypeError(f"mi can only be int or float, not {type(tonne)}")
            else:
                self.tonne = tonne

        def Metric_Tons_Milligrams(self):
            """
            Converts metric tons to milligrams
            """

            mg = self.tonne * 1000000000
            return mg

        def Metric_Tons_Kilogram(self):
            """
            Converts metric tons to kilograms and returns the number of kilograms
            """

            kg = self.tonne * 1000
            return kg

        def Metric_Tons_Grams(self):
            """
            Converts metric tons to grams and returns the number of grams
            """

            g = self.tonne * 1000000
            return g

        def Metric_Tons_Pounds(self):
            """
            Converts metric tons to pounds and returns the number of pounds
            """

            lb = self.tonne / 0.00045359237
            return lb

        def Metric_Tons_Ounces(self):
            """
            Converts metric tons to ounces and returns the number of ounces
            """

            oz = self.tonne / 0.0000283495231
            return oz

        def Metric_Tons_Short_Tons(self):
            """Converts metric tons to short tons (Also known as  US Tons) and returns the number of short tons"""

            st = self.tonne / 0.90718474
            return st

        def Metric_Tons_Long_Tons(self):
            """Converts metric tons to long tons (Also known as Imperial Tons) and returns the number of long tons"""

            lt = self.tonne / 1.01604691
            return lt

    class Short_Tons:
        def __init__(self, us_ton):
            if type(us_ton) is str:
                raise TypeError(f"mi can only be int or float, not {type(us_ton)}")
            else:
                self.us_ton = us_ton

        def Short_Tons_Milligrams(self):
            """
            Converts short tons to milligrams and returns the number of milligrams
            """

            mg = self.us_ton * 907184740
            return mg

        def Short_Tons_Pounds(self):
            """
            Converts tons to pounds and returns the number of pounds
            """

            lb = self.us_ton * 2000
            return lb

        def Short_Tons_Kilograms(self):
            """Converts tons to kilograms and returns the number of kilograms"""

            kg = self.us_ton * 907.18474
            return kg

        def Short_Tons_Grams(self):
            """
            Converts US tons to grams and returns the number of grams
            """

            g = self.us_ton * 907184.74
            return g

        def Short_Tons_Ounces(self):
            """
            Converts US tons to ounces and returns the number of ounces
            """

            oz = self.us_ton * 32000
            return oz

        def Short_Tons_Metric_Tons(self):
            """Converts short tons (Also known as US Tons) to metric tons and returns the number of metric tons"""

            tonnes = self.us_ton * 0.90718474
            return tonnes

        def Short_Tons_Long_Tons(self):
            """Converts short tons (Also known as US Tons) to long tons (Also known as Imperial Tons) and returns the number of long tons"""

            lt = self.us_ton / 1.12
            return lt

    class Long_Tons:
        def __init__(self, long_ton):
            if type(long_ton) is str:
                raise TypeError(f"mi can only be int or float, not {type(long_ton)}")
            else:
                self.long_ton = long_ton

        def Long_Tons_Pounds(self):
            """Converts long tons to pounds and returns the number of pounds"""

            lb = self.long_ton  * 2240
            return lb

        def Long_Tons_Kilograms(self):
            """Converts long tons to kilograms"""

            kg = self.long_ton * 1016.04691
            return kg

        def Long_Tons_Grams(self):
            """Converts long tons to grams and returns the number of grams"""

            g = self.long_ton * 1016046.91
            return g

        def Long_Tons_Ounces(self):
            """Converts long tons to ounces and returns the number of ounces"""

            oz = self.long_ton * 35840
            return oz

        def Long_Tons_Milligrams(self):
            """Converts long tons (Also known as Imperial Tons) to milligrams and returns the number of milligrams"""

            mg = self.long_ton * 1016046909
            return mg

        def Long_Tons_Metric_Tons(self):
            """Converts long tons (Also known as Imperial Tons) to metric tons and returns the number of metric tons"""

            tonnes = self.long_ton * 1.01604691
            return tonnes

        def Long_Tons_Short_Tons(self):
            """Converts long tons (Also known as imperial tons) to short tons (Also known a US Tons) and returns the number of short tons"""

            st = self.long_ton * 1.12
            return st
