import numpy as np
import pandas as pd

def makeFF10Indus(SIC):
    """
    PURPOSE: This function creates a Fama and French 10-industry classification index and a table with the industry
             names.
    :param SIC: Dataframe containing industry classifications, e.g. siccd
    :return:
            - FF10: dataframe with the industries indicators
            - FF10Names: table with the industry names
    """
    # 1 NoDur Consumer NonDurables -- Food, Tobacco, Textiles, Apparel, Leather, Toys
    FF10 = ((SIC >= 100) & (SIC <= 999)).astype(int)
    FF10 += ((SIC >= 2000) & (SIC <= 2399)).astype(int)
    FF10 += ((SIC >= 2700) & (SIC <= 2749)).astype(int)
    FF10 += ((SIC >= 2770) & (SIC <= 2799)).astype(int)
    FF10 += ((SIC >= 3100) & (SIC <= 3199)).astype(int)
    FF10 += ((SIC >= 3940) & (SIC <= 3989)).astype(int)

    # 2 Durbl Consumer Durables -- Cars, TV's, Furniture, Household Appliances
    FF10 += 2 * (((SIC >= 2500) & (SIC <= 2519)).astype(int))
    FF10 += 2 * (((SIC >= 2590) & (SIC <= 2599)).astype(int))
    FF10 += 2 * (((SIC >= 3630) & (SIC <= 3659)).astype(int))
    FF10 += 2 * (((SIC >= 3710) & (SIC <= 3711)).astype(int))
    FF10 += 2 * (((SIC == 3714)).astype(int))
    FF10 += 2 * (((SIC == 3716)).astype(int))
    FF10 += 2 * (((SIC >= 3750) & (SIC <= 3751)).astype(int))
    FF10 += 2 * (((SIC == 3792)).astype(int))
    FF10 += 2 * (((SIC >= 3900) & (SIC <= 3939)).astype(int))
    FF10 += 2 * (((SIC >= 3990) & (SIC <= 3999)).astype(int))

    # 3 Manuf Manufacturing -- Machinery, Trucks, Planes, Chemicals, Off Furn, Paper, Com Printing
    FF10 += 3 * (((SIC >= 2520) & (SIC <= 2589)).astype(int))
    FF10 += 3 * (((SIC >= 2600) & (SIC <= 2699)).astype(int))
    FF10 += 3 * (((SIC >= 2750) & (SIC <= 2769)).astype(int))
    FF10 += 3 * (((SIC >= 2800) & (SIC <= 2829)).astype(int))
    FF10 += 3 * (((SIC >= 3000) & (SIC <= 3099)).astype(int))
    FF10 += 3 * (((SIC >= 3200) & (SIC <= 3569)).astype(int))
    FF10 += 3 * (((SIC >= 3580) & (SIC <= 3621)).astype(int))
    FF10 += 3 * (((SIC >= 3623) & (SIC <= 3629)).astype(int))
    FF10 += 3 * (((SIC >= 3700) & (SIC <= 3709)).astype(int))
    FF10 += 3 * (((SIC >= 3712) & (SIC <= 3713)).astype(int))
    FF10 += 3 * (((SIC == 3715)).astype(int))
    FF10 += 3 * (((SIC >= 3717) & (SIC <= 3749)).astype(int))
    FF10 += 3 * (((SIC >= 3752) & (SIC <= 3791)).astype(int))
    FF10 += 3 * (((SIC >= 3793) & (SIC <= 3799)).astype(int))
    FF10 += 3 * (((SIC >= 3860) & (SIC <= 3899)).astype(int))

    # 4 Enrgy Oil, Gas, and Coal Extraction and Products
    FF10 += 4 * (((SIC >= 1200) & (SIC <= 1399)).astype(int))
    FF10 += 4 * (((SIC >= 2900) & (SIC <= 2999)).astype(int))

    #  5 HiTec  Business Equipment -- Computers, Software, and Electronic Equipment
    FF10 += 5*((SIC >=3570) & (SIC <= 3579))
    FF10 += 5*((SIC >=3622) & (SIC <= 3622))  # Industrial controls
    FF10 += 5*((SIC >=3660) & (SIC <= 3692))
    FF10 += 5*((SIC >=3694) & (SIC <= 3699))
    FF10 += 5*((SIC >=3810) & (SIC <= 3839))
    FF10 += 5*((SIC >=7370) & (SIC <= 7372))  # Services - computer programming and data processing
    FF10 += 5*((SIC >=7373) & (SIC <= 7373))  # Computer integrated systems design
    FF10 += 5*((SIC >=7374) & (SIC <= 7374))  # Services - computer processing, data prep
    FF10 += 5*((SIC >=7375) & (SIC <= 7375))  # Services - information retrieval services
    FF10 += 5*((SIC >=7376) & (SIC <= 7376))  # Services - computer facilities management service
    FF10 += 5*((SIC >=7377) & (SIC <= 7377))  # Services - computer rental and leasing
    FF10 += 5*((SIC >=7378) & (SIC <= 7378))  # Services - computer maintanence and repair
    FF10 += 5*((SIC >=7379) & (SIC <= 7379))  # Services - computer related services
    FF10 += 5*((SIC >=7391) & (SIC <= 7391))  # Services - R&D labs
    FF10 += 5*((SIC >=8730) & (SIC <= 8734))  # Services - research, development, testing labs


    # 6 Telcm Telephone and Television Transmission
    FF10 += 6*((SIC >=4800) & (SIC <= 4899))

    # 7 Shops Wholesale, Retail, and Some Services (Laundries, Repair Shops)
    FF10 += 7*((SIC >=5000) & (SIC <= 5999))
    FF10 += 7*((SIC >=7200) & (SIC <= 7299))
    FF10 += 7*((SIC >=7600) & (SIC <= 7699))

    # 8 Hlth Healthcare, Medical Equipment, and Drugs
    FF10 += 8*((SIC >=2830) & (SIC <= 2839))
    FF10 += 8*((SIC >=3693) & (SIC <= 3693))
    FF10 += 8*((SIC >=3840) & (SIC <= 3859))
    FF10 += 8*((SIC >=8000) & (SIC <= 8099))

    # 9 Utils Utilities
    FF10 += 9*((SIC >=4900) & (SIC <= 4949))

    # 10 Other Other -- Mines, Constr, BldMt, Trans, Hotels, Bus Serv, Entertainment, Finance
    FF10[(SIC > 0) & (FF10 == 0)] = 10

    # Store the FF10 industries and their names
    FF10Names = pd.DataFrame({
        'number': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'shortName': ['NoDur', 'Durbl', 'Manuf', 'Enrgy', 'HiTec', 'Telcm', 'Shops', 'Hlth', 'Utils', 'Other'],
        'longName': ['Consumer NonDurables', 'Consumer Durables', 'Manufacturing',
                     'Oil, Gas, and Coal Extraction and Products', 'Business Equipment',
                     'Telephone and Television Transmission', 'Wholesale, Retail, and Some Services',
                     'Healthcare, Medical Equipment, and Drugs', 'Utilities', 'Other']
    })
    FF10Names = FF10Names.set_index('number')

    return FF10, FF10Names

# test_indus, test_names = makeFF10Indus(SIC)



