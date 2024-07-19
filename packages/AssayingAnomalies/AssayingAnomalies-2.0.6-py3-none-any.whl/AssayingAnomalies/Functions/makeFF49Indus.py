import pandas as pd

def makeFF49Indus(SIC):
    def FF49_indus_mapping(SIC):
        # Agriculture
        if 100 <= SIC <= 299 or 700 <= SIC <= 799 or 910 <= SIC <= 919 or SIC == 2048:
            return 1

        # Food Products
        elif (2000 <= SIC <= 2046 or 2050 <= SIC <= 2063 or
              2070 <= SIC <= 2079 or 2090 <= SIC <= 2092 or
              SIC == 2095 or 2098 <= SIC <= 2099):
            return 2

        # Soda - Candy & Soda
        if ((2064 <= SIC <= 2068) or
                (SIC == 2086) or
                (SIC == 2087) or
                (SIC == 2096) or
                (SIC == 2097)):
            return 3

        # Beer - Beer & Liquor
        elif ((SIC == 2080) or
              (SIC == 2082) or
              (SIC == 2083) or
              (SIC == 2084) or
              (SIC == 2085)):
            return 4

        # Smoke - Tobacco Products
        elif 2100 <= SIC <= 2199:
            return 5

        # Toys - Recreation
        elif ((920 <= SIC <= 999) or
              (3650 <= SIC <= 3652) or
              (SIC == 3732) or
              (3930 <= SIC <= 3931) or
              (3940 <= SIC <= 3949)):
            return 6

        # Fun - Entertainment
        elif ((7800 <= SIC <= 7829) or
              (7830 <= SIC <= 7833) or
              (7840 <= SIC <= 7841) or
              (SIC == 7900) or
              (7910 <= SIC <= 7911) or
              (7920 <= SIC <= 7929) or
              (7930 <= SIC <= 7933) or
              (7940 <= SIC <= 7949) or
              (SIC == 7980) or
              (7990 <= SIC <= 7999)):
            return 7

        # Books - Printing and Publishing
        elif ((2700 <= SIC <= 2799) or
              (2770 <= SIC <= 2771) or
              (2780 <= SIC <= 2789)):
            return 8

        # Hshld - Consumer Goods
        elif ((SIC == 2047) or
              (2391 <= SIC <= 2392) or
              (2510 <= SIC <= 2599) or
              (2840 <= SIC <= 2844) or
              (3160 <= SIC <= 3172) or
              (3190 <= SIC <= 3199) or
              (SIC == 3229) or
              (SIC == 3260) or
              (3262 <= SIC <= 3263) or
              (SIC == 3269) or
              (3230 <= SIC <= 3231) or
              (3630 <= SIC <= 3639) or
              (3750 <= SIC <= 3751) or
              (SIC == 3800) or
              (3860 <= SIC <= 3873) or
              (3910 <= SIC <= 3915) or
              (3960 <= SIC <= 3962) or
              (SIC == 3991) or
              (SIC == 3995)):
            return 9

        # Clths - Apparel
        elif ((2300 <= SIC <= 2390) or
              (3020 <= SIC <= 3021) or
              (3100 <= SIC <= 3151) or
              (3963 <= SIC <= 3965)):
            return 10

        # Hlth - Healthcare
        elif 8000 <= SIC <= 8099:
            return 11

        # MedEq - Medical Equipment
        elif ((SIC == 3693) or
              (3840 <= SIC <= 3851)):
            return 12

        # Drugs - Pharmaceutical Products
        elif ((SIC >= 2830 and SIC <= 2831) or
              (2833 <= SIC <= 2836)):
            return 13

        # Chems - Chemicals
        elif ((2800 <= SIC <= 2829) or
              (2850 <= SIC <= 2879) or
              (2890 <= SIC <= 2899)):
            return 14

        # Rubbr - Rubber and Plastic Products
        elif ((SIC == 3031) or
              (SIC == 3041) or
              (3050 <= SIC <= 3099)):
            return 15

        # Txtls - Textiles
        elif ((2200 <= SIC <= 2299) or
              (2393 <= SIC <= 2399)):
            return 16

        # BldMt - Construction Materials
        elif ((800 <= SIC <= 899) or
              (2400 <= SIC <= 2499) or
              (2660 <= SIC <= 2661) or
              (2950 <= SIC <= 2952) or
              (3200 <= SIC <= 3299) or
              (3420 <= SIC <= 3452) or
              (3490 <= SIC <= 3499) or
              (SIC == 3996)):
            return 17

        # Cnstr - Construction
        elif ((1500 <= SIC <= 1549) or
              (1600 <= SIC <= 1799)):
            return 18

        # Steel - Steel Works Etc
        elif ((SIC == 3300) or
              (3310 <= SIC <= 3399)):
            return 19

        # FabPr - Fabricated Products
        elif ((SIC == 3400) or
              (3443 <= SIC <= 3479)):
            return 20

        # Mach - Machinery
        elif ((3510 <= SIC <= 3599) or
              (3580 <= SIC <= 3586) or
              (3589 <= SIC <= 3599)):
            return 21

        # ElcEq - Electrical Equipment
        elif ((SIC == 3600) or
              (3610 <= SIC <= 3699)):
            return 22

        # Autos - Automobiles and Trucks
        elif ((SIC == 2296) or
              (SIC == 2396) or
              (3010 <= SIC <= 3011) or
              (SIC == 3537) or
              (SIC == 3647) or
              (SIC == 3694) or
              (SIC == 3700) or
              (3710 <= SIC <= 3799)):
            return 23

        # Aero - Aircraft
        elif ((3720 <= SIC <= 3729)):
            return 24

        # Ships - Shipbuilding, Railroad Equipment
        elif ((3730 <= SIC <= 3731) or
              (3740 <= SIC <= 3743)):
            return 25

        # Guns - Defense
        elif ((3760 <= SIC <= 3769) or
              (SIC == 3795) or
              (3480 <= SIC <= 3489)):
            return 26

        # Gold - Precious Metals
        elif ((1040 <= SIC <= 1049)):
            return 27

        # Mines - Non-Metallic and Industrial Metal Mining
        elif ((1000 <= SIC <= 1039) or
              (1050 <= SIC <= 1119) or
              (1400 <= SIC <= 1499)):
            return 28

        # Coal - Coal
        elif ((1200 <= SIC <= 1299)):
            return 29

        # Oil - Petroleum and Natural Gas
        elif ((SIC == 1300) or
              (1310 <= SIC <= 1389) or
              (2900 <= SIC <= 2999)):
            return 30

        # Util - Utilities
        elif ((SIC == 4900) or
              (4910 <= SIC <= 4942)):
            return 31

        # Telcm - Communication
        elif ((SIC == 4800) or
              (4810 <= SIC <= 4899)):
            return 32

        # PerSv - Personal Services
        elif ((7020 <= SIC <= 7033) or
              (SIC == 7200) or
              (7210 <= SIC <= 7299) or
              (7395 <= SIC <= 7549) or
              (7600 <= SIC <= 7699) or
              (8100 <= SIC <= 8899) or
              (7510 <= SIC <= 7515)):
            return 33

        # BusSv - Business Services
        elif ((2750 <= SIC <= 2759) or
              (SIC == 3993) or
              (SIC == 7218) or
              (SIC == 7300) or
              (7310 <= SIC <= 8999) or
              (SIC == 7519) or
              (SIC == 8700) or
              (8710 <= SIC <= 8911) or
              (8920 <= SIC <= 8999) or
              (4220 <= SIC <= 4229)):
            return 34

        # Hardw - Computers
        elif ((3570 <= SIC <= 3579) or
              (3680 <= SIC <= 3695)):
            return 35

        # Softw - Computer Software
        elif ((7370 <= SIC <= 7373) or
              (SIC == 7375)):
            return 36

        # Chips - Electronic Equipment
        elif ((SIC == 3622) or
              (3661 <= SIC <= 3666) or
              (3669 <= SIC <= 3812)):
            return 37

        # LabEq - Measuring and Control Equipment
        elif ((SIC == 3811) or
              (3820 <= SIC <= 3827) or
              (3829 <= SIC <= 3839)):
            return 38
        # Paper - Business Supplies
        elif ((2520 <= SIC <= 2549) or
              (2600 <= SIC <= 2699) or
              (2760 <= SIC <= 2761) or
              (3950 <= SIC <= 3955)):
            return 39

        # Boxes - Shipping Containers
        elif ((2440 <= SIC <= 2449) or
              (2640 <= SIC <= 2659) or
              (3220 <= SIC <= 3221) or
              (3410 <= SIC <= 3412)):
            return 40

        # Trans - Transportation
        elif ((4000 <= SIC <= 4013) or
              (4040 <= SIC <= 4789)):
            return 41

        # Whlsl - Wholesale
        elif ((5000 <= SIC <= 5199)):
            return 42

        # Rtail - Retail
        elif ((5200 <= SIC <= 5999)):
            return 43

        # Meals - Restaurants, Hotels, Motels
        elif ((5800 <= SIC <= 7213)):
            return 44

        # Banks - Banking
        elif ((6000 <= SIC <= 6199)):
            return 45

        # Insur - Insurance
        elif ((6300 <= SIC <= 6411)):
            return 46

        # RlEst - Real Estate
        elif ((6500 <= SIC <= 6611)):
            return 47

        # Fin - Trading
        elif ((6200 <= SIC <= 6799)):
            return 48

        # Other - Almost Nothing
        elif ((4950 <= SIC <= 4991)):
            return 49

        else:
            return 0  # Return 0 or any other default value for unclassified industries

    FF49 = SIC.applymap(FF49_indus_mapping)

    data = {
        'shortName': ['Agric', 'Food', 'Soda', 'Beer', 'Smoke', 'Toys', 'Fun',
                      'Books', 'Hshld', 'Clths', 'Hlth', 'MedEq', 'Drugs', 'Chems',
                      'Rubbr', 'Txtls', 'BldMt', 'Cnstr', 'Steel', 'FabPr', 'Mach',
                      'ElcEq', 'Autos', 'Aero', 'Ships', 'Guns', 'Gold', 'Mines',
                      'Coal', 'Oil', 'Util', 'Telcm', 'PerSv', 'BusSv', 'Hardw',
                      'Softw', 'Chips', 'LabEq', 'Paper', 'Boxes', 'Trans', 'Whlsl',
                      'Rtail', 'Meals', 'Banks', 'Insur', 'RlEst', 'Fin', 'Other'],
        'longName': ['Agriculture', 'Food Products', 'Candy & Soda', 'Beer & Liquor',
                     'Tobacco Products', 'Recreation', 'Entertainment',
                     'Printing and Publishing', 'Consumer Goods', 'Apparel',
                     'Healthcare', 'Medical Equipment', 'Pharmaceutical Products',
                     'Chemicals', 'Rubber and Plastic Products', 'Textiles',
                     'Construction Materials', 'Construction', 'Steel Works Etc',
                     'Fabricated Products', 'Machinery', 'Electrical Equipment',
                     'Automobiles and Trucks', 'Aircraft', 'Shipbuilding, Railroad Equipment',
                     'Defense', 'Precious Metals', 'Non-Metallic and Industrial Metal Mining',
                     'Coal', 'Petroleum and Natural Gas', 'Utilities',
                     'Communication', 'Personal Services', 'Business Services',
                     'Computers', 'Computer Software', 'Electronic Equipment',
                     'Measuring and Control Equipment', 'Business Supplies',
                     'Shipping Containers', 'Transportation', 'Wholesale',
                     'Retail', 'Restaurants, Hotels, Motels', 'Banking',
                     'Insurance', 'Real Estate', 'Trading', 'Almost Nothing']
    }

    # Create the DataFrame of Industry names
    FF49_names = pd.DataFrame(data, index=range(1, 50))
    return FF49, FF49_names

# test1, test2 = makeFF49Indus(SIC)

