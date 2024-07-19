import pandas as pd


def makeFF17Indus(SIC):
    FF17 = 1 * ((SIC >= 100) & (SIC <= 299))
    FF17 += 1 * ((SIC >= 700) & (SIC <= 799))
    FF17 += 1 * ((SIC >= 900) & (SIC <= 999))
    FF17 += 1 * ((SIC >= 2000) & (SIC <= 2039))
    FF17 += 1 * (SIC >= 2040) & (SIC <= 2048)
    FF17 += 1 * (SIC >= 2050) & (SIC <= 2068)
    FF17 += 1 * (SIC >= 2070) & (SIC <= 2080)
    FF17 += 1 * ((SIC >= 2082) & (SIC <= 2087))
    FF17 += 1 * ((SIC >= 2090) & (SIC <= 2092))
    FF17 += 1 * ((SIC >= 2095) & (SIC <= 2099))
    FF17 += 1 * ((SIC >= 5140) & (SIC <= 5159))
    FF17 += 1 * ((SIC >= 5180) & (SIC <= 5182))
    FF17 += 1 * (SIC == 5191)

    # 2 Mines, Mining, and Minerals
    FF17 += 2 * ((SIC >= 1000) & (SIC <= 1049))
    FF17 += 2 * ((SIC >= 1060) & (SIC <= 1069))
    FF17 += 2 * ((SIC >= 1080) & (SIC <= 1099))
    FF17 += 2 * ((SIC >= 1200) & (SIC <= 1299))
    FF17 += 2 * ((SIC >= 1400) & (SIC <= 1499))
    FF17 += 2 * ((SIC >= 5050) & (SIC <= 5052))

    # 3 Oil, Oil and Petroleum Products
    FF17 += 3 * (SIC == 1300)
    FF17 += 3 * ((SIC >= 1310) & (SIC <= 1329))
    FF17 += 3 * ((SIC >= 1380) & (SIC <= 1382))
    FF17 += 3 * (SIC == 1389)
    FF17 += 3 * ((SIC >= 2900) & (SIC <= 2912))
    FF17 += 3 * ((SIC >= 5170) & (SIC <= 5172))

    # 4 Clths  Textiles, Apparel & Footware
    FF17 += 4 * ((SIC >= 2200) & (SIC <= 2284))
    FF17 += 4 * ((SIC >= 2290) & (SIC <= 2399))
    FF17 += 4 * ((SIC >= 3020) & (SIC <= 3021))
    FF17 += 4 * ((SIC >= 3100) & (SIC <= 3111))
    FF17 += 4 * ((SIC >= 3130) & (SIC <= 3131))
    FF17 += 4 * ((SIC >= 3140) & (SIC <= 3151))
    FF17 += 4 * ((SIC >= 3963) & (SIC <= 3965))
    FF17 += 4 * ((SIC >= 5130) & (SIC <= 5139))

    # 5 Durbl  Consumer Durables
    FF17 += 5 * ((SIC >= 2510) & (SIC <= 2519))
    FF17 += 5 * ((SIC >= 2590) & (SIC <= 2599))
    FF17 += 5 * ((SIC >= 3060) & (SIC <= 3099))
    FF17 += 5 * ((SIC >= 3630) & (SIC <= 3639))
    FF17 += 5 * ((SIC >= 3650) & (SIC <= 3652))
    FF17 += 5 * ((SIC >= 3860) & (SIC <= 3861))
    FF17 += 5 * ((SIC >= 3870) & (SIC <= 3873))
    FF17 += 5 * ((SIC >= 3910) & (SIC <= 3911))
    FF17 += 5 * ((SIC >= 3914) & (SIC == 3915))
    FF17 += 5 * ((SIC >= 3930) & (SIC <= 3931))
    FF17 += 5 * ((SIC >= 3940) & (SIC <= 3949))
    FF17 += 5 * ((SIC >= 3960) & (SIC <= 3962))
    FF17 += 5 * ((SIC >= 5020) & (SIC <= 5023))
    FF17 += 5 * (SIC == 5064)
    FF17 += 5 * (SIC == 5094)
    FF17 += 5 * (SIC == 5099)

    # 6 Chems Chemicals
    FF17 += 6 * ((SIC >= 2800) & (SIC <= 2829))
    FF17 += 6 * ((SIC >= 2860) & (SIC <= 2899))
    FF17 += 6 * ((SIC >= 5160) & (SIC <= 5169))

    # 7 Cnsum Drugs, Soap, Prfums, Tobacco
    FF17 += 7 * ((SIC >= 2100) & (SIC <= 2199))
    FF17 += 7 * ((SIC >= 2830) & (SIC <= 2831))
    FF17 += 7 * (SIC == 2833)
    FF17 += 7 * (SIC == 2834)
    FF17 += 7 * ((SIC >= 2840) & (SIC <= 2844))
    FF17 += 7 * ((SIC >= 5120) & (SIC <= 5122))
    FF17 += 7 * (SIC == 5194)

    # 8 Cnstr Construction and Construction Materials
    FF17 += 8 * ((SIC >= 800) & (SIC <= 899))
    FF17 += 8 * ((SIC >= 1500) & (SIC <= 1511))
    FF17 += 8 * ((SIC >= 1520) & (SIC <= 1549))
    FF17 += 8 * ((SIC >= 1600) & (SIC <= 1799))
    FF17 += 8 * ((SIC >= 2400) & (SIC <= 2459))
    FF17 += 8 * ((SIC >= 2490) & (SIC <= 2499))
    FF17 += 8 * ((SIC >= 2850) & (SIC <= 2859))
    FF17 += 8 * ((SIC >= 2950) & (SIC <= 2952))
    FF17 += 8 * (SIC == 3200)
    FF17 += 8 * ((SIC >= 3210) & (SIC <= 3211))
    FF17 += 8 * ((SIC >= 3240) & (SIC <= 3241))
    FF17 += 8 * ((SIC >= 3250) & (SIC <= 3259))
    FF17 += 8 * (SIC == 3261)
    FF17 += 8 * (SIC == 3264)
    FF17 += 8 * ((SIC >= 3270) & (SIC <= 3275))
    FF17 += 8 * ((SIC >= 3280) & (SIC <= 3281))
    FF17 += 8 * ((SIC >= 3290) & (SIC <= 3293))
    FF17 += 8 * ((SIC >= 3420) & (SIC <= 3429))
    FF17 += 8 * ((SIC >= 3430) & (SIC <= 3433))
    FF17 += 8 * ((SIC >= 3440) & (SIC <= 3442))
    FF17 += 8 * (SIC == 3446)
    FF17 += 8 * ((SIC >= 3448) & (SIC <= 3452))
    FF17 += 8 * ((SIC >= 5030) & (SIC <= 5039))
    FF17 += 8 * ((SIC >= 5070) & (SIC <= 5078))
    FF17 += 8 * (SIC == 5198)
    FF17 += 8 * ((SIC >= 5210) & (SIC <= 5211))
    FF17 += 8 * ((SIC >= 5230) & (SIC <= 5231))
    FF17 += 8 * ((SIC >= 5250) & (SIC <= 5251))

    # 9 Steel  Steel Works Etc	 & SIC <=
    FF17 += 9 * (SIC == 3300)
    FF17 += 9 * ((SIC >= 3310) & (SIC <= 3317))
    FF17 += 9 * ((SIC >= 3320) & (SIC <= 3325))
    FF17 += 9 * ((SIC >= 3330) & (SIC <= 3341))
    FF17 += 9 * ((SIC >= 3350) & (SIC <= 3357))
    FF17 += 9 * ((SIC >= 3360) & (SIC <= 3369))
    FF17 += 9 * ((SIC >= 3390) & (SIC <= 3399))

    # 10 FabPr  Fabricated Products	 & SIC <=
    FF17 += 10 * ((SIC >= 3410) & (SIC <= 3412))
    FF17 += 10 * ((SIC >= 3443) & (SIC <= 3444))
    FF17 += 10 * ((SIC >= 3460) & (SIC <= 3499))

    # 	11 Machn  Machinery and Business Equipment	 & SIC <=
    FF17 += 11 * ((SIC >= 3510) & (SIC <= 3536))
    FF17 += 11 * ((SIC >= 3540) & (SIC <= 3600))
    FF17 += 11 * ((SIC >= 3610) & (SIC <= 3613))
    FF17 += 11 * ((SIC >= 3620) & (SIC <= 3629))
    FF17 += 11 * ((SIC >= 3670) & (SIC <= 3695))
    FF17 += 11 * (SIC == 3699)
    FF17 += 11 * ((SIC >= 3810) & (SIC <= 3812))
    FF17 += 11 * ((SIC >= 3820) & (SIC <= 3839))
    FF17 += 11 * ((SIC >= 3950) & (SIC <= 3955))
    FF17 += 11 * (SIC == 5060)
    FF17 += 11 * (SIC == 5063)
    FF17 += 11 * (SIC == 5065)
    FF17 += 11 * (SIC == 5080)
    FF17 += 11 * (SIC == 5081)

    # 12 Cars, Automobiles
    FF17 += 12 * ((SIC >= 3710) & (SIC <= 3711))
    FF17 += 12 * (SIC == 3714)
    FF17 += 12 * (SIC == 3716)
    FF17 += 12 * ((SIC >= 3750) & (SIC <= 3751))
    FF17 += 12 * (SIC == 3792)
    FF17 += 12 * ((SIC >= 5010) & (SIC <= 5015))
    FF17 += 12 * ((SIC >= 5510) & (SIC <= 5521))
    FF17 += 12 * ((SIC >= 5530) & (SIC <= 5531))
    FF17 += 12 * ((SIC >= 5560) & (SIC <= 5561))
    FF17 += 12 * ((SIC >= 5570) & (SIC <= 5571))
    FF17 += 12 * ((SIC >= 5590) & (SIC <= 5599))

    # 13 Transportation
    FF17 += 13 * (SIC == 3713)
    FF17 += 13 * (SIC == 3715)
    FF17 += 13 * (SIC == 3720)
    FF17 += 13 * (SIC == 3721)
    FF17 += 13 * ((SIC >= 3724) & (SIC <= 3725))
    FF17 += 13 * (SIC == 3728)
    FF17 += 13 * ((SIC >= 3730) & (SIC <= 3732))
    FF17 += 13 * ((SIC >= 3740) & (SIC <= 3743))
    FF17 += 13 * ((SIC >= 3760) & (SIC <= 3769))
    FF17 += 13 * (SIC == 3790)
    FF17 += 13 * (SIC == 3795)
    FF17 += 13 * (SIC == 3799)
    FF17 += 13 * ((SIC >= 4000) & (SIC <= 4013))
    FF17 += 13 * (SIC == 4100)
    FF17 += 13 * ((SIC >= 4110) & (SIC <= 4121))
    FF17 += 13 * ((SIC >= 4130) & (SIC <= 4131))
    FF17 += 13 * ((SIC >= 4140) & (SIC <= 4142))
    FF17 += 13 * ((SIC >= 4150) & (SIC <= 4151))
    FF17 += 13 * ((SIC >= 4170) & (SIC <= 4173))
    FF17 += 13 * ((SIC >= 4190) & (SIC <= 4200))
    FF17 += 13 * ((SIC >= 4210) & (SIC <= 4231))
    FF17 += 13 * ((SIC >= 4400) & (SIC <= 4700))
    FF17 += 13 * ((SIC >= 4710) & (SIC <= 4712))
    FF17 += 13 * ((SIC >= 4720) & (SIC <= 4742))
    FF17 += 13 * (SIC == 4780)
    FF17 += 13 * (SIC == 4783)
    FF17 += 13 * (SIC == 4785)
    FF17 += 13 * (SIC == 4789)

    # 14 Utils Utilities
    FF17 += 14 * (SIC == 4900)
    FF17 += 14 * ((SIC >= 4910) & (SIC <= 4911))
    FF17 += 14 * ((SIC >= 4920) & (SIC <= 4925))
    FF17 += 14 * ((SIC >= 4930) & (SIC <= 4932))
    FF17 += 14 * ((SIC >= 4939) & (SIC <= 4942))

    # 15 Retail Retail Stores
    FF17 += 15 * ((SIC >= 5260) & (SIC <= 5261))
    FF17 += 15 * ((SIC >= 5270) & (SIC <= 5271))
    FF17 += 15 * (SIC == 5300)
    FF17 += 15 * ((SIC >= 5310) & (SIC <= 5311))
    FF17 += 15 * (SIC == 5320)
    FF17 += 15 * ((SIC >= 5330) & (SIC <= 5331))
    FF17 += 15 * (SIC == 5334)
    FF17 += 15 * ((SIC >= 5390) & (SIC <= 5400))
    FF17 += 15 * ((SIC >= 5410) & (SIC <= 5412))
    FF17 += 15 * ((SIC >= 5420) & (SIC <= 5421))
    FF17 += 15 * ((SIC >= 5430) & (SIC <= 5431))
    FF17 += 15 * ((SIC >= 5440) & (SIC <= 5441))
    FF17 += 15 * ((SIC >= 5450) & (SIC <= 5451))
    FF17 += 15 * ((SIC >= 5460) & (SIC <= 5461))
    FF17 += 15 * ((SIC >= 5490) & (SIC <= 5499))
    FF17 += 15 * ((SIC >= 5540) & (SIC <= 5541))
    FF17 += 15 * ((SIC >= 5550) & (SIC <= 5551))
    FF17 += 15 * ((SIC >= 5600) & (SIC <= 5700))
    FF17 += 15 * ((SIC >= 5710) & (SIC <= 5722))
    FF17 += 15 * ((SIC >= 5730) & (SIC <= 5736))
    FF17 += 15 * (SIC == 5750)
    FF17 += 15 * ((SIC >= 5800) & (SIC <= 5813))
    FF17 += 15 * (SIC == 5890)
    FF17 += 15 * (SIC == 5900)
    FF17 += 15 * ((SIC >= 5910) & (SIC <= 5912))
    FF17 += 15 * ((SIC >= 5920) & (SIC <= 5921))
    FF17 += 15 * ((SIC >= 5930) & (SIC <= 5932))
    FF17 += 15 * ((SIC >= 5940) & (SIC <= 5949))
    FF17 += 15 * ((SIC >= 5960) & (SIC <= 5963))
    FF17 += 15 * ((SIC >= 5980) & (SIC <= 5990))
    FF17 += 15 * ((SIC >= 5992) & (SIC <= 5995))
    FF17 += 15 * (SIC == 5999)

    # 16 Finan Banks, Insurance Companies, and Other Financials
    FF17 += 16 * ((SIC >= 6010) & (SIC <= 6023))
    FF17 += 16 * ((SIC >= 6025) & (SIC <= 6026))
    FF17 += 16 * ((SIC >= 6028) & (SIC <= 6036))
    FF17 += 16 * ((SIC >= 6040) & (SIC <= 6062))
    FF17 += 16 * ((SIC >= 6080) & (SIC <= 6082))
    FF17 += 16 * ((SIC >= 6090) & (SIC <= 6100))
    FF17 += 16 * ((SIC >= 6110) & (SIC <= 6112))
    FF17 += 16 * ((SIC >= 6120) & (SIC <= 6129))
    FF17 += 16 * ((SIC >= 6140) & (SIC <= 6163))
    FF17 += 16 * (SIC == 6172)
    FF17 += 16 * ((SIC >= 6199) & (SIC <= 6300))
    FF17 += 16 * ((SIC >= 6310) & (SIC <= 6312))
    FF17 += 16 * ((SIC >= 6320) & (SIC <= 6324))
    FF17 += 16 * ((SIC >= 6330) & (SIC <= 6331))
    FF17 += 16 * ((SIC >= 6350) & (SIC <= 6351))
    FF17 += 16 * ((SIC >= 6360) & (SIC <= 6361))
    FF17 += 16 * ((SIC >= 6370) & (SIC <= 6371))
    FF17 += 16 * ((SIC >= 6390) & (SIC <= 6411))
    FF17 += 16 * (SIC == 6500)
    FF17 += 16 * (SIC == 6510)
    FF17 += 16 * ((SIC >= 6512) & (SIC <= 6515))
    FF17 += 16 * ((SIC >= 6517) & (SIC <= 6519))
    FF17 += 16 * ((SIC >= 6530) & (SIC <= 6532))
    FF17 += 16 * ((SIC >= 6540) & (SIC <= 6541))
    FF17 += 16 * ((SIC >= 6550) & (SIC <= 6553))
    FF17 += 16 * (SIC == 6611)
    FF17 += 16 * (SIC == 6700)
    FF17 += 16 * ((SIC >= 6710) & (SIC <= 6726))
    FF17 += 16 * ((SIC >= 6730) & (SIC <= 6733))
    FF17 += 16 * (SIC == 6790)
    FF17 += 16 * (SIC == 6792)
    FF17 += 16 * ((SIC >= 6794) & (SIC <= 6795))
    FF17 += 16 * ((SIC >= 6798) & (SIC <= 6799))

    # 17 Other
    FF17[((SIC > 0) & (FF17 == 0))] = 17

    # Store the FF17 industries and their names
    FF17Names = [[1, 'Food', 'Food'],
                 [2, 'Mines', 'Mining and Minerals'],
                 [3, 'Oil', 'Oil and Petroleum Products'],
                 [4, 'Clths', 'Textiles, Apparel & Footware'],
                 [5, 'Durbl', 'Consumer Durables'],
                 [6, 'Chems', 'Chemicals'],
                 [7, 'Cnsum', 'Drugs, Soap, Prfums, Tobacco'],
                 [8, 'Cnstr', 'Construction and Construction Materials'],
                 [9, 'Steel', 'Steel Works Etc'],
                 [10, 'FabPr', 'Fabricated Products'],
                 [11, 'Machn', 'Machinery and Business Equipment'],
                 [12, 'Cars', 'Automobiles'],
                 [13, 'Trans', 'Transportation'],
                 [14, 'Utils', 'Utilities'],
                 [15, 'Rtail', 'Retail Stores'],
                 [16, 'Finan', 'Banks, Insurance Companies, and Other Financials'],
                 [17, 'Other', 'Almost Nothing']]
    FF17Names = pd.DataFrame(FF17Names, columns=['number', 'shortName', 'longName']).set_index('number')

    return FF17, FF17Names