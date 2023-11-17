import boto3
import csv


client = boto3.client('account')
response = client.list_regions(RegionOptStatusContains=['ENABLED','ENABLED_BY_DEFAULT'])
allRegions = []
for i in response['Regions']:
	allRegions.append(i['RegionName'])

client = boto3.client('sts')
response = client.get_caller_identity()
accountID = response['Account']

dictArr = []

client = boto3.client('route53', region_name='us-east-1')
response = client.list_hosted_zones()

for i in response['HostedZones']:
    dict = {}
    dict['Id'] = i['Id']
    dict['Name'] = i['Name']
    dict['ResourceRecordSetCount'] = i['ResourceRecordSetCount']
    dict['IS_PRIVATE'] = i['Config']['PrivateZone']
    dict['Type'] = 'HostedZone'
    dict['AccountID'] = accountID
    dict['DomainName'] = ''
    dict['AutoRenew'] = ''
    dict['Expiry'] = ''
    dictArr.append(dict)

client = boto3.client('route53domains',region_name='us-east-1')
response = client.list_domains()

for i in response['Domains']:
    dict = {}
    dict['Id'] = ''
    dict['Name'] = ''
    dict['ResourceRecordSetCount'] = ''
    dict['IS_PRIVATE'] = ''
    dict['Type'] = 'Domain'
    dict['DomainName'] = i['DomainName']
    dict['AutoRenew'] = i['AutoRenew']
    dict['Expiry'] = i['Expiry']    
    dictArr.append(dict)

with open("outputR53-"+accountID+".csv", "w") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames = dict.keys())
    writer.writeheader()
    
    for i in dictArr:
        writer.writerow(i)
    

