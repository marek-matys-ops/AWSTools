import boto3
import json
import csv


"""
To run it run AWS CloudShell, upload this file and run it with command: 

python3 inventoryEC2.py

Download using CloudShell -> Actions -> Download file ( put: outputE2-accountID.csv )
"""

client = boto3.client('account')
response = client.list_regions(RegionOptStatusContains=['ENABLED','ENABLED_BY_DEFAULT'])
allRegions = []
for i in response['Regions']:
	allRegions.append(i['RegionName'])

client = boto3.client('sts')
response = client.get_caller_identity()
accountID = response['Account']

dict = {}
dictArr = []

for iter in range(0, len(allRegions)):	
	client = boto3.client('ec2',region_name=allRegions[iter])			
	response = client.describe_instances()	
	
	
	for instance in response['Reservations']:
		instanceId = instance['Instances'][0]['InstanceId']
	
		dict = {}

		dict['ID'] = instance['Instances'][0]['InstanceId']
		dict['Type'] = instance['Instances'][0]['InstanceType']
		dict['amiId'] = instance['Instances'][0]['ImageId']
		dict['securityGroups'] = instance['Instances'][0]['SecurityGroups']
		#securityGroupsList = []
		#for i in securityGroups:
	#		securityGroupsList.append(i['GroupId'])
		try:
			dict['Public_IP'] = instance['Instances'][0]['PublicIpAddress']		
		except:
			dict['Public_IP'] = 'NoIP'
		dict['Private_IP'] = instance['Instances'][0]['PrivateIpAddress']		
		instanceTags = instance['Instances'][0]['Tags']
		instanceTagsList = []		
		dict['Name'] = 'NoName'
		for i in instanceTags:
			if i['Key'] == 'Name':
				dict['Name'] = i['Value']
			instanceTagsList.append(i['Key']+":"+i['Value'])
		dict['TagsList'] = instanceTagsList
		dict['region'] = allRegions[iter]
		dict['accountID'] = accountID
		dictArr.append(dict)

print(dictArr)    

if dictArr == []:
	print("No instances found")
	exit()


out_filename = "outputEC2-"+accountID+".csv"

with open(out_filename, "w") as csv_file:
	writer = csv.DictWriter(csv_file, fieldnames = dictArr[0].keys())

	writer.writeheader()	
	for iter in dictArr:
		writer.writerow(iter)
