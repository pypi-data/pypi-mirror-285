from master_converter.conversions import Length

def test_millimeters():
    assert str(Length.Millimeters(1).Millimeters_Miles()) == "6.21371192237334e-07"
    assert str(Length.Millimeters(2).Millimeters_Miles()) == "1.242742384474668e-06"
    assert str(Length.Millimeters(3).Millimeters_Miles()) == "1.864113576712002e-06"

    assert str(Length.Millimeters(1).Millimeters_Yards()) == "0.0010936132983377078"
    assert str(Length.Millimeters(2).Millimeters_Yards()) == "0.0021872265966754157"
    assert str(Length.Millimeters(3).Millimeters_Yards()) == "0.0032808398950131233"

    assert str(Length.Millimeters(1).Millimeters_Inches()) == "0.03937007874015748"
    assert str(Length.Millimeters(2).Millimeters_Inches()) == "0.07874015748031496"
    assert str(Length.Millimeters(3).Millimeters_Inches()) == "0.11811023622047245"

    assert str(Length.Millimeters(1).Millimeters_Meters()) == "0.001"
    assert str(Length.Millimeters(2).Millimeters_Meters()) == "0.002"
    assert str(Length.Millimeters(3).Millimeters_Meters()) == "0.003"

    assert str(Length.Millimeters(1).Millimeters_Feet()) == "0.0032808398950131233"
    assert str(Length.Millimeters(2).Millimeters_Feet()) == "0.006561679790026247"
    assert str(Length.Millimeters(3).Millimeters_Feet()) == "0.00984251968503937"

    assert str(Length.Millimeters(1).Millimeters_Centimeters()) == "0.1"
    assert str(Length.Millimeters(2).Millimeters_Centimeters()) == "0.2"
    assert str(Length.Millimeters(3).Millimeters_Centimeters()) == "0.3"

    assert str(Length.Millimeters(1).Millimeters_Kilometers()) == "1e-06"
    assert str(Length.Millimeters(2).Millimeters_Kilometers()) == "2e-06"
    assert str(Length.Millimeters(3).Millimeters_Kilometers()) == "3e-06"

    assert str(Length.Millimeters(1).Millimeters_Nautical_Miles()) == "5.399568034557235e-07"
    assert str(Length.Millimeters(2).Millimeters_Nautical_Miles()) == "1.079913606911447e-06"
    assert str(Length.Millimeters(3).Millimeters_Nautical_Miles()) == "1.6198704103671705e-06"

def test_centimeters():
    assert str(Length.Centimeters(1).Centimeters_Meters()) == "0.01"
    assert str(Length.Centimeters(2).Centimeters_Meters()) == "0.02"
    assert str(Length.Centimeters(3).Centimeters_Meters()) == "0.03"

    assert str(Length.Centimeters(1).Centimeters_Millimeters()) == "10"
    assert str(Length.Centimeters(2).Centimeters_Millimeters()) == "20"
    assert str(Length.Centimeters(3).Centimeters_Millimeters()) == "30"

    assert str(Length.Centimeters(1).Centimeters_Kilometers()) == "1e-05"
    assert str(Length.Centimeters(2).Centimeters_Kilometers()) == "2e-05"
    assert str(Length.Centimeters(3).Centimeters_Kilometers()) == "3e-05"

    assert str(Length.Centimeters(1).Centimeters_Miles()) == "6.21371192237334e-06"
    assert str(Length.Centimeters(2).Centimeters_Miles()) == "1.242742384474668e-05"
    assert str(Length.Centimeters(3).Centimeters_Miles()) == "1.864113576712002e-05"

    assert str(Length.Centimeters(1).Centimeters_Yards()) == "0.010936132983377079"
    assert str(Length.Centimeters(2).Centimeters_Yards()) == "0.021872265966754158"
    assert str(Length.Centimeters(3).Centimeters_Yards()) == "0.03280839895013123"

    assert str(Length.Centimeters(1).Centimeters_Feet()) == "0.03280839895013123"
    assert str(Length.Centimeters(2).Centimeters_Feet()) == "0.06561679790026247"
    assert str(Length.Centimeters(3).Centimeters_Feet()) == "0.09842519685039369"

    assert str(Length.Centimeters(1).Centimeters_Inches()) == "0.39370078740157477"
    assert str(Length.Centimeters(2).Centimeters_Inches()) == "0.7874015748031495"
    assert str(Length.Centimeters(3).Centimeters_Inches()) == "1.1811023622047243"

    assert str(Length.Centimeters(1).Centimeters_Nautical_Miles()) == "5.399568034557236e-06"
    assert str(Length.Centimeters(2).Centimeters_Nautical_Miles()) == "1.0799136069114471e-05"
    assert str(Length.Centimeters(3).Centimeters_Nautical_Miles()) == "1.6198704103671705e-05"

def test_meters():
    assert str(Length.Meters(1).Meters_Millimeters()) == "1000"
    assert str(Length.Meters(2).Meters_Millimeters()) == "2000"
    assert str(Length.Meters(3).Meters_Millimeters()) == "3000"

    assert str(Length.Meters(1).Meters_Centimeters()) == "100"
    assert str(Length.Meters(2).Meters_Centimeters()) == "200"
    assert str(Length.Meters(3).Meters_Centimeters()) == "300"

    assert str(Length.Meters(1).Meters_Kilometers()) == "0.001"
    assert str(Length.Meters(2).Meters_Kilometers()) == "0.002"
    assert str(Length.Meters(3).Meters_Kilometers()) == "0.003"

    assert str(Length.Meters(1).Meters_Inches()) == "39.37007874015748"
    assert str(Length.Meters(2).Meters_Inches()) == "78.74015748031496"
    assert str(Length.Meters(3).Meters_Inches()) == "118.11023622047244"

    assert str(Length.Meters(1).Meters_Feet()) == "3.280839895013123"
    assert str(Length.Meters(2).Meters_Feet()) == "6.561679790026246"
    assert str(Length.Meters(3).Meters_Feet()) == "9.84251968503937"

    assert str(Length.Meters(1).Meters_Yards()) == "1.0936132983377078"
    assert str(Length.Meters(2).Meters_Yards()) == "2.1872265966754156"
    assert str(Length.Meters(3).Meters_Yards()) == "3.2808398950131235"

    assert str(Length.Meters(1).Meters_Miles()) == "0.0006213711922373339"
    assert str(Length.Meters(2).Meters_Miles()) == "0.0012427423844746678"
    assert str(Length.Meters(3).Meters_Miles()) == "0.0018641135767120019"

    assert str(Length.Meters(1).Meters_Nautical_Miles()) == "0.0005399568034557236"
    assert str(Length.Meters(2).Meters_Nautical_Miles()) == "0.0010799136069114472"
    assert str(Length.Meters(3).Meters_Nautical_Miles()) == "0.0016198704103671706"

def test_kilometers():
    assert str(Length.Kilometers(1).Kilometers_Millimeters()) == "1000000"
    assert str(Length.Kilometers(2).Kilometers_Millimeters()) == "2000000"
    assert str(Length.Kilometers(3).Kilometers_Millimeters()) == "3000000"

    assert str(Length.Kilometers(1).Kilometers_Centimeters()) == "100000"
    assert str(Length.Kilometers(2).Kilometers_Centimeters()) == "200000"
    assert str(Length.Kilometers(3).Kilometers_Centimeters()) == "300000"

    assert str(Length.Kilometers(1).Kilometers_Meters()) == "1000"
    assert str(Length.Kilometers(2).Kilometers_Meters()) == "2000"
    assert str(Length.Kilometers(3).Kilometers_Meters()) == "3000"

    assert str(Length.Kilometers(1).Kilometers_Inches()) == "39370.07874015748"
    assert str(Length.Kilometers(2).Kilometers_Inches()) == "78740.15748031496"
    assert str(Length.Kilometers(3).Kilometers_Inches()) == "118110.23622047243"

    assert str(Length.Kilometers(1).Kilometers_Feet()) == "3280.8398950131236"
    assert str(Length.Kilometers(2).Kilometers_Feet()) == "6561.679790026247"
    assert str(Length.Kilometers(3).Kilometers_Feet()) == "9842.519685039371"

    assert str(Length.Kilometers(1).Kilometers_Yards()) == "1093.6132983377079"
    assert str(Length.Kilometers(2).Kilometers_Yards()) == "2187.2265966754157"
    assert str(Length.Kilometers(3).Kilometers_Yards()) == "3280.839895013123"

    assert str(Length.Kilometers(1).Kilometers_Miles()) == "0.621371192237334"
    assert str(Length.Kilometers(2).Kilometers_Miles()) == "1.242742384474668"
    assert str(Length.Kilometers(3).Kilometers_Miles()) == "1.8641135767120018"

    assert str(Length.Kilometers(1).Kilometers_Nautical_Miles()) == "0.5399568034557235"
    assert str(Length.Kilometers(2).Kilometers_Nautical_Miles()) == "1.079913606911447"
    assert str(Length.Kilometers(3).Kilometers_Nautical_Miles()) == "1.6198704103671706"

def test_inches():
    assert str(Length.Inches(1).Inches_Millimeters()) == "25.4"
    assert str(Length.Inches(2).Inches_Millimeters()) == "50.8"
    assert str(Length.Inches(3).Inches_Millimeters()) == "76.19999999999999"

    assert str(Length.Inches(1).Inches_Centimeters()) == "2.54"
    assert str(Length.Inches(2).Inches_Centimeters()) == "5.08"
    assert str(Length.Inches(3).Inches_Centimeters()) == "7.62"

    assert str(Length.Inches(1).Inches_Meters()) == "0.0254"
    assert str(Length.Inches(2).Inches_Meters()) == "0.0508"
    assert str(Length.Inches(3).Inches_Meters()) == "0.07619999999999999"

    assert str(Length.Inches(1).Inches_Kilometers()) == "2.54e-05"
    assert str(Length.Inches(2).Inches_Kilometers()) == "5.08e-05"
    assert str(Length.Inches(3).Inches_Kilometers()) == "7.620000000000001e-05"

    assert str(Length.Inches(1).Inches_Feet()) == "0.08333333333333333"
    assert str(Length.Inches(2).Inches_Feet()) == "0.16666666666666666"
    assert str(Length.Inches(3).Inches_Feet()) == "0.25"

    assert str(Length.Inches(1).Inches_Yards()) == "0.027777777777777776"
    assert str(Length.Inches(2).Inches_Yards()) == "0.05555555555555555"
    assert str(Length.Inches(3).Inches_Yards()) == "0.08333333333333333"

    assert str(Length.Inches(1).Inches_Miles()) == "1.5782828282828283e-05"
    assert str(Length.Inches(2).Inches_Miles()) == "3.1565656565656566e-05"
    assert str(Length.Inches(3).Inches_Miles()) == "4.734848484848485e-05"

    assert str(Length.Inches(1).Inches_Nautical_Miles()) == "1.3714902812811087e-05"
    assert str(Length.Inches(2).Inches_Nautical_Miles()) == "2.7429805625622174e-05"
    assert str(Length.Inches(3).Inches_Nautical_Miles()) == "4.114470843843326e-05"

def test_feet():
    assert str(Length.Feet(1).Feet_Millimeters()) == "304.8"
    assert str(Length.Feet(2).Feet_Millimeters()) == "609.6"
    assert str(Length.Feet(3).Feet_Millimeters()) == "914.4000000000001"

    assert str(Length.Feet(1).Feet_Centimeters()) == "30.48"
    assert str(Length.Feet(2).Feet_Centimeters()) == "60.96"
    assert str(Length.Feet(3).Feet_Centimeters()) == "91.44"

    assert str(Length.Feet(1).Feet_Meters()) == "0.3048"
    assert str(Length.Feet(2).Feet_Meters()) == "0.6096"
    assert str(Length.Feet(3).Feet_Meters()) == "0.9144000000000001"

    assert str(Length.Feet(1).Feet_Kilometers()) == "0.0003048"
    assert str(Length.Feet(2).Feet_Kilometers()) == "0.0006096"
    assert str(Length.Feet(3).Feet_Kilometers()) == "0.0009143999999999999"

    assert str(Length.Feet(1).Feet_Inches()) == "12"
    assert str(Length.Feet(2).Feet_Inches()) == "24"
    assert str(Length.Feet(3).Feet_Inches()) == "36"

    assert str(Length.Feet(1).Feet_Yards()) == "0.3333333333333333"
    assert str(Length.Feet(2).Feet_Yards()) == "0.6666666666666666"
    assert str(Length.Feet(3).Feet_Yards()) == "1.0"

    assert str(Length.Feet(1).Feet_Miles()) == "0.0001893939393939394"
    assert str(Length.Feet(2).Feet_Miles()) == "0.0003787878787878788"
    assert str(Length.Feet(3).Feet_Miles()) == "0.0005681818181818182"

    assert str(Length.Feet(1).Feet_Nautical_Miles()) == "0.00016457883357315844"
    assert str(Length.Feet(2).Feet_Nautical_Miles()) == "0.0003291576671463169"
    assert str(Length.Feet(3).Feet_Nautical_Miles()) == "0.0004937365007194753"

def test_yards():
    assert str(Length.Yards(1).Yards_Millimeters()) == "914.4"
    assert str(Length.Yards(2).Yards_Millimeters()) == "1828.8"
    assert str(Length.Yards(3).Yards_Millimeters()) == "2743.2"

    assert str(Length.Yards(1).Yards_Centimeters()) == "91.44"
    assert str(Length.Yards(2).Yards_Centimeters()) == "182.88"
    assert str(Length.Yards(3).Yards_Centimeters()) == "274.32"

    assert str(Length.Yards(1).Yards_Meters()) == "0.9144"
    assert str(Length.Yards(2).Yards_Meters()) == "1.8288"
    assert str(Length.Yards(3).Yards_Meters()) == "2.7432"

    assert str(Length.Yards(1).Yards_Kilometers()) == "0.0009144"
    assert str(Length.Yards(2).Yards_Kilometers()) == "0.0018288"
    assert str(Length.Yards(3).Yards_Kilometers()) == "0.0027432"

    assert str(Length.Yards(1).Yards_Inches()) == "36"
    assert str(Length.Yards(2).Yards_Inches()) == "72"
    assert str(Length.Yards(3).Yards_Inches()) == "108"

    assert str(Length.Yards(1).Yards_Feet()) == "3"
    assert str(Length.Yards(2).Yards_Feet()) == "6"
    assert str(Length.Yards(3).Yards_Feet()) == "9"

    assert str(Length.Yards(1).Yards_Miles()) == "0.0005681818181818182"
    assert str(Length.Yards(2).Yards_Miles()) == "0.0011363636363636363"
    assert str(Length.Yards(3).Yards_Miles()) == "0.0017045454545454545"

    assert str(Length.Yards(1).Yards_Nautical_Miles()) == "0.0004937365007194753"
    assert str(Length.Yards(2).Yards_Nautical_Miles()) == "0.0009874730014389505"
    assert str(Length.Yards(3).Yards_Nautical_Miles()) == "0.0014812095021584258"

def test_miles():
    assert str(Length.Miles(1).Miles_Millimeters()) == "1609344"
    assert str(Length.Miles(2).Miles_Millimeters()) == "3218688"
    assert str(Length.Miles(3).Miles_Millimeters()) == "4828032"

    assert str(Length.Miles(1).Miles_Centimeters()) == "160934.4"
    assert str(Length.Miles(2).Miles_Centimeters()) == "321868.8"
    assert str(Length.Miles(3).Miles_Centimeters()) == "482803.19999999995"

    assert str(Length.Miles(1).Miles_Meters()) == "1609.344"
    assert str(Length.Miles(2).Miles_Meters()) == "3218.688"
    assert str(Length.Miles(3).Miles_Meters()) == "4828.032"

    assert str(Length.Miles(1).Miles_Kilometers()) == "1.609344"
    assert str(Length.Miles(2).Miles_Kilometers()) == "3.218688"
    assert str(Length.Miles(3).Miles_Kilometers()) == "4.828032"

    assert str(Length.Miles(1).Miles_Inches()) == "63360"
    assert str(Length.Miles(2).Miles_Inches()) == "126720"
    assert str(Length.Miles(3).Miles_Inches()) == "190080"

    assert str(Length.Miles(1).Miles_Feet()) == "5280"
    assert str(Length.Miles(2).Miles_Feet()) == "10560"
    assert str(Length.Miles(3).Miles_Feet()) == "15840"

    assert str(Length.Miles(1).Miles_Yards()) == "1760"
    assert str(Length.Miles(2).Miles_Yards()) == "3520"
    assert str(Length.Miles(3).Miles_Yards()) == "5280"

    assert str(Length.Miles(1).Miles_Nautical_Miles()) == "0.868975825092546"
    assert str(Length.Miles(2).Miles_Nautical_Miles()) == "1.737951650185092"
    assert str(Length.Miles(3).Miles_Nautical_Miles()) == "2.606927475277638"

def test_nautical_miles():
    assert str(Length.Nautical_Miles(1).Nautical_Miles_Millimeters()) == "1852000"
    assert str(Length.Nautical_Miles(2).Nautical_Miles_Millimeters()) == "3704000"
    assert str(Length.Nautical_Miles(3).Nautical_Miles_Millimeters()) == "5556000"

    assert str(Length.Nautical_Miles(1).Nautical_Miles_Centimeters()) == "185200"
    assert str(Length.Nautical_Miles(2).Nautical_Miles_Centimeters()) == "370400"
    assert str(Length.Nautical_Miles(3).Nautical_Miles_Centimeters()) == "555600"

    assert str(Length.Nautical_Miles(1).Nautical_Miles_Meters()) == "1852"
    assert str(Length.Nautical_Miles(2).Nautical_Miles_Meters()) == "3704"
    assert str(Length.Nautical_Miles(3).Nautical_Miles_Meters()) == "5556"

    assert str(Length.Nautical_Miles(1).Nautical_Miles_Kilometers()) == "1.852"
    assert str(Length.Nautical_Miles(2).Nautical_Miles_Kilometers()) == "3.704"
    assert str(Length.Nautical_Miles(3).Nautical_Miles_Kilometers()) == "5.556"

    assert str(Length.Nautical_Miles(1).Nautical_Miles_Inches()) == "72913.3858"
    assert str(Length.Nautical_Miles(2).Nautical_Miles_Inches()) == "145826.7716"
    assert str(Length.Nautical_Miles(3).Nautical_Miles_Inches()) == "218740.15740000003"

    assert str(Length.Nautical_Miles(1).Nautical_Miles_Feet()) == "6076.11549"
    assert str(Length.Nautical_Miles(2).Nautical_Miles_Feet()) == "12152.23098"
    assert str(Length.Nautical_Miles(3).Nautical_Miles_Feet()) == "18228.34647"

    assert str(Length.Nautical_Miles(1).Nautical_Miles_Yards()) == "2025.37183"
    assert str(Length.Nautical_Miles(2).Nautical_Miles_Yards()) == "4050.74366"
    assert str(Length.Nautical_Miles(3).Nautical_Miles_Yards()) == "6076.11549"

    assert str(Length.Nautical_Miles(1).Nautical_Miles_Miles()) == "1.15078"
    assert str(Length.Nautical_Miles(2).Nautical_Miles_Miles()) == "2.30156"
    assert str(Length.Nautical_Miles(3).Nautical_Miles_Miles()) == "3.4523399999999995"