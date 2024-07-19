# AssayingAnomalies

## Contents of This File

- Introduction
- Requirements
- Setup
- Usage
- Acknowledgements
- References

## Introduction

Please cite Novy-Marx and Velikov (2023) when using this repository. [https://papers.ssrn.com/abstract=4338007]

Authors: Joshua Lawson (jlaws13@simon.rochester.edu)

This repository contains the Python Toolkit that accompanies Novy-Marx and Velikov (2023), intended for empirical academic asset pricing research, particularly focused on studying anomalies in the cross-section of stock returns. After setting up several parameters, the toolkit automatically downloads return data from CRSP and accounting data from COMPUSTAT through a WRDS connection, storing the data for further analysis.

The Python Toolkit includes functions demonstrating how to conduct standard tests in empirical asset pricing research, such as univariate and portfolio sorts and Fama-MacBeth cross-sectional regressions.

For more information, see the companion website at [http://assayinganomalies.com].

## Requirements

To use the library fully, you need:

 - A WRDS subscription with access to Monthly and Daily CRSP, Annual and Quarterly COMPUSTAT, CRSP/COMPUSTAT merged database.
 - Python 3.8 or newer.
 - Required Python packages (listed in requirements.txt).
## Setup

Follow these steps to install and set up the AssayingAnomalies package for use:

### 1. Environment Preparation

Before installing the AssayingAnomalies package, ensure you are working in the desired Python environment. If necessary, create and activate a new environment using your preferred environment manager (e.g., conda, virtualenv).

### 2. Installing the Package

Install the AssayingAnomalies package using pip by running the following command in your terminal or command prompt:

pip install AssayingAnomalies

### 3. Running the Initial Setup

After installation, initiate the setup process to configure your settings and prepare for data download and processing. Open a new python file and execute the following:

from AssayingAnomalies import initial_setup \
initial_setup()

During this setup, you will be prompted to enter various parameters, including your WRDS credentials and preferences for data handling.

### 4. Data Download and Processing

Upon completing the initial setup, you can choose to proceed with the data download and processing immediately or postpone it for later.

To Proceed Immediately: Simply follow the prompts in the initial setup process.

To Postpone and Resume Later: If you decide to download and process the data later, execute the following commands when you're ready:

from AssayingAnomalies.setup_library import download_and_process_data \
download_and_process_data()

## Setup Example (CIRC): 
Open up the terminal and type the following commands.
- module load anaconda3/5.3.0b 
- conda create --name name_your_environment python=3.8 
- conda activate name_your_environment
- pip install AssayingAnomalies
- python3
- from AssayingAnomalies import initial_setup
- initial_setup

Then follow the on-screen prompts and wait for the setup to complete. 

## Hardware Recommendations

High-Performance Computing: While the initial setup can be completed on a personal computer, the data processing tasks are designed to run in parallel, significantly benefiting from high-performance computing resources. We highly recommend running the data download and processing on your institution's high-performance computing system, e.g. CIRC if at the University of Rochester. 

System Requirements: For optimal performance, request access to a system with at least 12 CPUs and 112GB of RAM. If possible, request more resources to ensure the process runs smoothly.

Processing Time: Expect the data processing to take approximately 4 hours to complete, depending on the system's capabilities and the specific parameters you've set.

## Usage

Once the data download and processing are complete, you're ready to utilize the Toolkit's functionality. For examples and guidance on how to use the Toolkit, refer to the use_library.py script included with the package.  This script provides examples of conducting empirical asset pricing tests, including univariate and double portfolio sorts and Fama-MacBeth cross-sectional regression.

## Acknowledgements

We thank Andrea Frazzini for sharing scripts that inspired some of our code organization. Special thanks to Don Bowen, Andrew Detzel, Ulas Misirli, Rob Parham, Haowei Yuan, and PhD students at Penn State University and the University of Rochester for their helpful comments and for testing earlier versions.

## References

- Chen, A. and M. Velikov, 2021, "Zeroing in on the Expected Returns of Anomalies," Journal of Financial and Quantitative Analysis, Forthcoming.
- Hasbrouck, J., 2009, "Trading Costs and Returns for U.S. Equities: Estimating Effective Costs from Daily Data, Journal of Finance, 64, 1445-1477
- Novy-Marx, R. and M. Velikov, 2023, Assaying Anomalies, Working Paper
- Ozdagli, A. and M. Velikov, 2020, Show Me the Money: The Monetary Policy Risk Premium, Journal of Financial Economics, 143 (1),80-106

