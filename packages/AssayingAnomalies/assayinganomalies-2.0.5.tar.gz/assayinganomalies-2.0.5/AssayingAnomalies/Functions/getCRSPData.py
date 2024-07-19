import wrds
from datetime import datetime
import os

def getCRSPData(params):
    username = params.username
    crsp_csv_file_path = params.crspFolder + os.sep
    start = params.sample_start
    end = params.sample_end
    "Establish connection to WRDS"
    db = wrds.Connection(wrds_username=username)

    "Timekeeping"
    print(f"\nNow working on collecting data from CRSP. Run started at {datetime.now()}.\n")

    """Want to download and save the following tables from CRSP:
     MSFHDR, MSF, MSEDELIST, MSEEXCHDATES, CCMXPF_LNKHIST, STOCKNAMES"""

    crsp_msfhdr = db.raw_sql("select * from CRSP.MSFHDR")
    crsp_msfhdr.to_csv(crsp_csv_file_path + 'crsp_msfhdr.csv')

    crsp_msf = db.raw_sql(f"select * from CRSP.MSF where date>='01/01/{start}' and date<='12/31/{end}'")

    crsp_msf.to_csv(crsp_csv_file_path + 'crsp_msf.csv')

    crsp_msedelist = db.raw_sql("select * from CRSP.MSEDELIST")
    crsp_msedelist.to_csv(crsp_csv_file_path + 'crsp_msedelist.csv')

    crsp_mseexchdates = db.raw_sql("select * from CRSP.MSEEXCHDATES")
    crsp_mseexchdates.to_csv(crsp_csv_file_path + 'crsp_mseexchdates.csv')

    crsp_ccmxpf_lnkhist = db.raw_sql("select * from CRSP.CCMXPF_LNKHIST")
    crsp_ccmxpf_lnkhist.to_csv(crsp_csv_file_path + 'crsp_ccmxpf_lnkhist.csv')

    crsp_stocknames = db.raw_sql("select * from CRSP.STOCKNAMES")
    crsp_stocknames.to_csv(crsp_csv_file_path + 'crsp_stocknames.csv')

    "Timekeeping"
    print(f"\nFinished collecting data from CRSP. Run ended at {datetime.now()}.\n")

    db.close()

# import wrds


#
# "Set path"
# crspFolder = r'/home/jlaws13/PycharmProjects/AssayingAnomalies_root/Data/CRSP/'
#
# "Establish connection to WRDS"
# db = wrds.Connection(wrds_username='jlaws13')
#
# """Want to download and save the following tables from CRSP:
#  MSFHDR, MSF, MSEDELIST, MSEEXCHDATES, CCMXPF_LNKHIST, STOCKNAMES"""
#
#
# crsp_msfhdr = db.raw_sql("select * from CRSP.MSFHDR")
# crsp_msfhdr.to_csv(crspFolder + 'crsp_msfhdr.csv')
#
# crsp_msf = db.raw_sql("select * from CRSP.MSF")
# crsp_msf.to_csv(r'C:\Users\josh\OneDrive - University at Buffalo\Desktop\Spring_2023\Empirical_Asset_Pricing\AssayingAnomalies\Data\crsp_msf.csv')
#
# crsp_msedelist = db.raw_sql("select * from CRSP.MSEDELIST")
# crsp_msedelist.to_csv(r'C:\Users\josh\OneDrive - University at Buffalo\Desktop\Spring_2023\Empirical_Asset_Pricing\AssayingAnomalies\Data\crsp_msedelist.csv')
#
# crsp_mseexchdates = db.raw_sql("select * from CRSP.MSEEXCHDATES")
# crsp_mseexchdates.to_csv(r'C:\Users\josh\OneDrive - University at Buffalo\Desktop\Spring_2023\Empirical_Asset_Pricing\AssayingAnomalies\Data\crsp_mseexchdates.csv')
#
# crsp_ccmxpf_lnkhist = db.raw_sql("select * from CRSP.CCMXPF_LNKHIST")
# crsp_ccmxpf_lnkhist.to_csv(r'C:\Users\josh\OneDrive - University at Buffalo\Desktop\Spring_2023\Empirical_Asset_Pricing\AssayingAnomalies\Data\crsp_ccmxpf_lnkhist.csv')
#
# crsp_stocknames = db.raw_sql("select * from CRSP.STOCKNAMES")
# crsp_stocknames.to_csv(r'C:\Users\josh\OneDrive - University at Buffalo\Desktop\Spring_2023\Empirical_Asset_Pricing\AssayingAnomalies\Data\crsp_stocknames.csv')
#
# db.close()

