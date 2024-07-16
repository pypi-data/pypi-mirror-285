from master_converter.conversions import Mass

def test_milligrams():
    assert str(Mass.Milligrams(1).Milligrams_Grams()) == "0.001"
    assert str(Mass.Milligrams(2).Milligrams_Grams()) == "0.002"
    assert str(Mass.Milligrams(3).Milligrams_Grams()) == "0.003"

    assert str(Mass.Milligrams(1).Milligrams_Kilograms()) == "1e-06"
    assert str(Mass.Milligrams(2).Milligrams_Kilograms()) == "2e-06"
    assert str(Mass.Milligrams(3).Milligrams_Kilograms()) == "3e-06"

    assert str(Mass.Milligrams(1).Milligrams_Ounces()) == "3.5273961980686725e-05"
    assert str(Mass.Milligrams(2).Milligrams_Ounces()) == "7.054792396137345e-05"
    assert str(Mass.Milligrams(3).Milligrams_Ounces()) == "0.00010582188594206017"

    assert str(Mass.Milligrams(1).Milligrams_Pounds()) == "2.204622621848776e-06"
    assert str(Mass.Milligrams(2).Milligrams_Pounds()) == "4.409245243697552e-06"
    assert str(Mass.Milligrams(3).Milligrams_Pounds()) == "6.613867865546328e-06"

    assert str(Mass.Milligrams(1).Milligrams_Metric_Tons()) == "1e-09"
    assert str(Mass.Milligrams(2).Milligrams_Metric_Tons()) == "2e-09"
    assert str(Mass.Milligrams(3).Milligrams_Metric_Tons()) == "3e-09"

    assert str(Mass.Milligrams(1).Milligrams_Short_Tons()) == "1.102311310924388e-09"
    assert str(Mass.Milligrams(2).Milligrams_Short_Tons()) == "2.204622621848776e-09"
    assert str(Mass.Milligrams(3).Milligrams_Short_Tons()) == "3.3069339327731637e-09"

    assert str(Mass.Milligrams(1).Milligrams_Long_Tons()) == "9.842065274173282e-10"
    assert str(Mass.Milligrams(2).Milligrams_Long_Tons()) == "1.9684130548346564e-09"
    assert str(Mass.Milligrams(3).Milligrams_Long_Tons()) == "2.952619582251984e-09"

def test_grams():
    assert str(Mass.Grams(1).Grams_Milligrams()) == "1000"
    assert str(Mass.Grams(2).Grams_Milligrams()) == "2000"
    assert str(Mass.Grams(3).Grams_Milligrams()) == "3000"

    assert str(Mass.Grams(1).Grams_Kilograms()) == "0.001"
    assert str(Mass.Grams(2).Grams_Kilograms()) == "0.002"
    assert str(Mass.Grams(3).Grams_Kilograms()) == "0.003"

    assert str(Mass.Grams(1).Grams_Ounces()) == "0.035273961980686726"
    assert str(Mass.Grams(2).Grams_Ounces()) == "0.07054792396137345"
    assert str(Mass.Grams(3).Grams_Ounces()) == "0.10582188594206017"

    assert str(Mass.Grams(1).Grams_Pounds()) == "0.002204622621848776"
    assert str(Mass.Grams(2).Grams_Pounds()) == "0.004409245243697552"
    assert str(Mass.Grams(3).Grams_Pounds()) == "0.006613867865546327"

    assert str(Mass.Grams(1).Grams_Metric_Tons()) == "1e-06"
    assert str(Mass.Grams(2).Grams_Metric_Tons()) == "2e-06"
    assert str(Mass.Grams(3).Grams_Metric_Tons()) == "3e-06"

    assert str(Mass.Grams(1).Grams_Short_Tons()) == "1.102311310924388e-06"
    assert str(Mass.Grams(2).Grams_Short_Tons()) == "2.204622621848776e-06"
    assert str(Mass.Grams(3).Grams_Short_Tons()) == "3.306933932773164e-06"

    assert str(Mass.Grams(1).Grams_Long_Tons()) == "9.842065264486655e-07"
    assert str(Mass.Grams(2).Grams_Long_Tons()) == "1.968413052897331e-06"
    assert str(Mass.Grams(3).Grams_Long_Tons()) == "2.9526195793459967e-06"

def test_Kilograms():
    assert str(Mass.Kilograms(1).Kilograms_Milligrams()) == "1000000"
    assert str(Mass.Kilograms(2).Kilograms_Milligrams()) == "2000000"
    assert str(Mass.Kilograms(3).Kilograms_Milligrams()) == "3000000"

    assert str(Mass.Kilograms(1).Kilograms_Grams()) == "1000"
    assert str(Mass.Kilograms(2).Kilograms_Grams()) == "2000"
    assert str(Mass.Kilograms(3).Kilograms_Grams()) == "3000"

    assert str(Mass.Kilograms(1).Kilograms_Ounces()) == "35.27396198068672"
    assert str(Mass.Kilograms(2).Kilograms_Ounces()) == "70.54792396137344"
    assert str(Mass.Kilograms(3).Kilograms_Ounces()) == "105.82188594206018"

    assert str(Mass.Kilograms(1).Kilograms_Pounds()) == "2.2046226218487757"
    assert str(Mass.Kilograms(2).Kilograms_Pounds()) == "4.409245243697551"
    assert str(Mass.Kilograms(3).Kilograms_Pounds()) == "6.613867865546327"

    assert str(Mass.Kilograms(1).Kilograms_Metric_Tons()) == "0.001"
    assert str(Mass.Kilograms(2).Kilograms_Metric_Tons()) == "0.002"
    assert str(Mass.Kilograms(3).Kilograms_Metric_Tons()) == "0.003"

    assert str(Mass.Kilograms(1).Kilograms_Short_Tons()) == "0.001102311310924388"
    assert str(Mass.Kilograms(2).Kilograms_Short_Tons()) == "0.002204622621848776"
    assert str(Mass.Kilograms(3).Kilograms_Short_Tons()) == "0.0033069339327731636"

    assert str(Mass.Kilograms(1).Kilograms_Long_Tons()) == "0.0009842065264486655"
    assert str(Mass.Kilograms(2).Kilograms_Long_Tons()) == "0.001968413052897331"
    assert str(Mass.Kilograms(3).Kilograms_Long_Tons()) == "0.002952619579345997"

def test_ounces():
    assert str(Mass.Ounces(1).Ounces_Milligrams()) == "28349.5231"
    assert str(Mass.Ounces(2).Ounces_Milligrams()) == "56699.0462"
    assert str(Mass.Ounces(3).Ounces_Milligrams()) == "85048.5693"

    assert str(Mass.Ounces(1).Ounces_Grams()) == "28.3495231"
    assert str(Mass.Ounces(2).Ounces_Grams()) == "56.6990462"
    assert str(Mass.Ounces(3).Ounces_Grams()) == "85.0485693"

    assert str(Mass.Ounces(1).Ounces_Kilograms()) == "0.0283495231"
    assert str(Mass.Ounces(2).Ounces_Kilograms()) == "0.0566990462"
    assert str(Mass.Ounces(3).Ounces_Kilograms()) == "0.0850485693"

    assert str(Mass.Ounces(1).Ounces_Pounds()) == "0.0625"
    assert str(Mass.Ounces(2).Ounces_Pounds()) == "0.125"
    assert str(Mass.Ounces(3).Ounces_Pounds()) == "0.1875"

    assert str(Mass.Ounces(1).Ounces_Metric_Tons()) == "2.83495231e-05"
    assert str(Mass.Ounces(2).Ounces_Metric_Tons()) == "5.66990462e-05"
    assert str(Mass.Ounces(3).Ounces_Metric_Tons()) == "8.504856930000001e-05"

    assert str(Mass.Ounces(1).Ounces_Short_Tons()) == "3.125e-05"
    assert str(Mass.Ounces(2).Ounces_Short_Tons()) == "6.25e-05"
    assert str(Mass.Ounces(3).Ounces_Short_Tons()) == "9.375e-05"

    assert str(Mass.Ounces(1).Ounces_Long_Tons()) == "2.7901785714285713e-05"
    assert str(Mass.Ounces(2).Ounces_Long_Tons()) == "5.580357142857143e-05"
    assert str(Mass.Ounces(3).Ounces_Long_Tons()) == "8.370535714285714e-05"

def test_pounds():
    assert str(Mass.Pounds(1).Pounds_Milligrams()) == "453592.37"
    assert str(Mass.Pounds(2).Pounds_Milligrams()) == "907184.74"
    assert str(Mass.Pounds(3).Pounds_Milligrams()) == "1360777.1099999999"

    assert str(Mass.Pounds(1).Pounds_Grams()) == "453.59237"
    assert str(Mass.Pounds(2).Pounds_Grams()) == "907.18474"
    assert str(Mass.Pounds(3).Pounds_Grams()) == "1360.77711"

    assert str(Mass.Pounds(1).Pounds_kilograms()) == "0.45359237"
    assert str(Mass.Pounds(2).Pounds_kilograms()) == "0.90718474"
    assert str(Mass.Pounds(3).Pounds_kilograms()) == "1.3607771100000001"

    assert str(Mass.Pounds(1).Pounds_Ounces()) == "16"
    assert str(Mass.Pounds(2).Pounds_Ounces()) == "32"
    assert str(Mass.Pounds(3).Pounds_Ounces()) == "48"

    assert str(Mass.Pounds(1).Pounds_Metric_Tons()) == "0.00045359237"
    assert str(Mass.Pounds(2).Pounds_Metric_Tons()) == "0.00090718474"
    assert str(Mass.Pounds(3).Pounds_Metric_Tons()) == "0.00136077711"

    assert str(Mass.Pounds(1).Pounds_Short_Tons()) == "0.0005"
    assert str(Mass.Pounds(2).Pounds_Short_Tons()) == "0.001"
    assert str(Mass.Pounds(3).Pounds_Short_Tons()) == "0.0015"

    assert str(Mass.Pounds(1).Pounds_Long_Tons()) == "0.0004464285714285714"
    assert str(Mass.Pounds(2).Pounds_Long_Tons()) == "0.0008928571428571428"
    assert str(Mass.Pounds(3).Pounds_Long_Tons()) == "0.0013392857142857143"

def test_metric_tons():
    assert str(Mass.Metric_Tons(1).Metric_Tons_Milligrams()) == "1000000000"
    assert str(Mass.Metric_Tons(2).Metric_Tons_Milligrams()) == "2000000000"
    assert str(Mass.Metric_Tons(3).Metric_Tons_Milligrams()) == "3000000000"

    assert str(Mass.Metric_Tons(1).Metric_Tons_Grams()) == "1000000"
    assert str(Mass.Metric_Tons(2).Metric_Tons_Grams()) == "2000000"
    assert str(Mass.Metric_Tons(3).Metric_Tons_Grams()) == "3000000"

    assert str(Mass.Metric_Tons(1).Metric_Tons_Kilogram()) == "1000"
    assert str(Mass.Metric_Tons(2).Metric_Tons_Kilogram()) == "2000"
    assert str(Mass.Metric_Tons(3).Metric_Tons_Kilogram()) == "3000"

    assert str(Mass.Metric_Tons(1).Metric_Tons_Ounces()) == "35273.96198068672"
    assert str(Mass.Metric_Tons(2).Metric_Tons_Ounces()) == "70547.92396137344"
    assert str(Mass.Metric_Tons(3).Metric_Tons_Ounces()) == "105821.88594206017"

    assert str(Mass.Metric_Tons(1).Metric_Tons_Pounds()) == "2204.622621848776"
    assert str(Mass.Metric_Tons(2).Metric_Tons_Pounds()) == "4409.245243697552"
    assert str(Mass.Metric_Tons(3).Metric_Tons_Pounds()) == "6613.867865546327"

    assert str(Mass.Metric_Tons(1).Metric_Tons_Short_Tons()) == "1.1023113109243878"
    assert str(Mass.Metric_Tons(2).Metric_Tons_Short_Tons()) == "2.2046226218487757"
    assert str(Mass.Metric_Tons(3).Metric_Tons_Short_Tons()) == "3.3069339327731635"

    assert str(Mass.Metric_Tons(1).Metric_Tons_Long_Tons()) == "0.9842065264486656"
    assert str(Mass.Metric_Tons(2).Metric_Tons_Long_Tons()) == "1.9684130528973312"
    assert str(Mass.Metric_Tons(3).Metric_Tons_Long_Tons()) == "2.952619579345997"

def test_short_tons():
    assert str(Mass.Short_Tons(1).Short_Tons_Milligrams()) == "907184740"
    assert str(Mass.Short_Tons(2).Short_Tons_Milligrams()) == "1814369480"
    assert str(Mass.Short_Tons(3).Short_Tons_Milligrams()) == "2721554220"

    assert str(Mass.Short_Tons(1).Short_Tons_Grams()) == "907184.74"
    assert str(Mass.Short_Tons(2).Short_Tons_Grams()) == "1814369.48"
    assert str(Mass.Short_Tons(3).Short_Tons_Grams()) == "2721554.2199999997"

    assert str(Mass.Short_Tons(1).Short_Tons_Kilograms()) == "907.18474"
    assert str(Mass.Short_Tons(2).Short_Tons_Kilograms()) == "1814.36948"
    assert str(Mass.Short_Tons(3).Short_Tons_Kilograms()) == "2721.55422"

    assert str(Mass.Short_Tons(1).Short_Tons_Ounces()) == "32000"
    assert str(Mass.Short_Tons(2).Short_Tons_Ounces()) == "64000"
    assert str(Mass.Short_Tons(3).Short_Tons_Ounces()) == "96000"

    assert str(Mass.Short_Tons(1).Short_Tons_Pounds()) == "2000"
    assert str(Mass.Short_Tons(2).Short_Tons_Pounds()) == "4000"
    assert str(Mass.Short_Tons(3).Short_Tons_Pounds()) == "6000"

    assert str(Mass.Short_Tons(1).Short_Tons_Metric_Tons()) == "0.90718474"
    assert str(Mass.Short_Tons(2).Short_Tons_Metric_Tons()) == "1.81436948"
    assert str(Mass.Short_Tons(3).Short_Tons_Metric_Tons()) == "2.7215542200000002"

    assert str(Mass.Short_Tons(1).Short_Tons_Long_Tons()) == "0.8928571428571428"
    assert str(Mass.Short_Tons(2).Short_Tons_Long_Tons()) == "1.7857142857142856"
    assert str(Mass.Short_Tons(3).Short_Tons_Long_Tons()) == "2.6785714285714284"

def test_long_tons():
    assert str(Mass.Long_Tons(1).Long_Tons_Milligrams()) == "1016046909"
    assert str(Mass.Long_Tons(2).Long_Tons_Milligrams()) == "2032093818"
    assert str(Mass.Long_Tons(3).Long_Tons_Milligrams()) == "3048140727"

    assert str(Mass.Long_Tons(1).Long_Tons_Grams()) == "1016046.91"
    assert str(Mass.Long_Tons(2).Long_Tons_Grams()) == "2032093.82"
    assert str(Mass.Long_Tons(3).Long_Tons_Grams()) == "3048140.73"

    assert str(Mass.Long_Tons(1).Long_Tons_Kilograms()) == "1016.04691"
    assert str(Mass.Long_Tons(2).Long_Tons_Kilograms()) == "2032.09382"
    assert str(Mass.Long_Tons(3).Long_Tons_Kilograms()) == "3048.14073"

    assert str(Mass.Long_Tons(1).Long_Tons_Ounces()) == "35840"
    assert str(Mass.Long_Tons(2).Long_Tons_Ounces()) == "71680"
    assert str(Mass.Long_Tons(3).Long_Tons_Ounces()) == "107520"

    assert str(Mass.Long_Tons(1).Long_Tons_Pounds()) == "2240"
    assert str(Mass.Long_Tons(2).Long_Tons_Pounds()) == "4480"
    assert str(Mass.Long_Tons(3).Long_Tons_Pounds()) == "6720"

    assert str(Mass.Long_Tons(1).Long_Tons_Metric_Tons()) == "1.01604691"
    assert str(Mass.Long_Tons(2).Long_Tons_Metric_Tons()) == "2.03209382"
    assert str(Mass.Long_Tons(3).Long_Tons_Metric_Tons()) == "3.04814073"

    assert str(Mass.Long_Tons(1).Long_Tons_Short_Tons()) == "1.12"
    assert str(Mass.Long_Tons(2).Long_Tons_Short_Tons()) == "2.24"
    assert str(Mass.Long_Tons(3).Long_Tons_Short_Tons()) == "3.3600000000000003"