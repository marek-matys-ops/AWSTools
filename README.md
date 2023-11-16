# AWSTools

Requirements: Python3 ( boto3 lib), git, AWS CloudShell has it pre-installed. 

To run it just open AWS Cloud shell and clone this repository:

git clone https://github.com/marek-matys/AWSTools

Then go to AWSTools directory: 

cd AWSTools

### inventory.py
Script to collect some of services for all available regions. Output is a CSV table ( comma separated ). Should be run via AWS Cloud Shell.
Run:
python3 inventory.py

### inventoryEC2
Script to collect the EC2 basic inventory from all available regions. Output is a CSV table ( comma separated). Should be run via AWS Cloud Shell.
Run:
python3 inventory.py