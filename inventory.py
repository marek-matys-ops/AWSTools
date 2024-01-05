import boto3
import json
import csv
import logging
import threading
import time
import random
import sys

"""
To run it run AWS CloudShell, upload this file and run it with command: 

python3 inventory.py

Download using CloudShell -> Actions -> Download file ( put: output.csv )
"""

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(asctime)s: %(message)s')

dict = {}

###################### Account ######################

clientAccount = boto3.client('account')
response = clientAccount.list_regions(RegionOptStatusContains=['ENABLED','ENABLED_BY_DEFAULT'])
allRegions = []
for i in response['Regions']:
	allRegions.append(i['RegionName'])

################# S3 ######################

'''
client = boto3.client('s3')
s3namesArr = []
s3regionsArr = []
response = client.list_buckets()
dict['S3'] = [len(response['Buckets'])]
for i in response['Buckets']:
	s3namesArr.append(i['Name'])
for i in s3namesArr:
	location = client.get_bucket_location(Bucket=i)['LocationConstraint']
	if location == None:
		s3regionsArr.append('us-east-1')
	else:
		s3regionsArr.append(location)

print(dict)

out_filename = "output.csv"

with open(out_filename, "w") as csv_file:
	writer = csv.writer(csv_file)
	
	writer.writerow(["ServiceName","Global"]+allRegions)
	for iter in dict:
		writer.writerow([iter]+dict[iter])
'''
###################### Threads ######################	
def get_client(service_name,region_name):
	try:
		# check if service is available in region
		return boto3.client(service_name,region_name=region_name)
	except:
		return None
# service_name, Region, is_global, response_name
services = [	
	# ["ec2", "EC2", "describe_instances()", False, "Reservations"],
	# ["s3", "S3", "list_buckets()", False, "Buckets"],
	# ["vpc", "VPC", "describe_vpcs()", False, "Vpcs"],
	# ["vpn", "VPN", "describe_vpn_connections()", False, "VpnConnections"],
	# ["subnet", "SUBNETS", "describe_subnets()", False, "Subnets"],
	# ["sg", "SG", "describe_security_groups()", False, "SecurityGroups"],
	# ["r53", "R53", "get_hosted_zone_count()", True, "HostedZoneCount"],
	# ["acm", "ACM", "list_certificates()", False, "CertificateSummaryList"],
	#  ["apigw_http", "API_GW_HTTP", "get_apis()", False, "Items",None],
	#  ["apigw_edge", "API_GW_EDGE", "get_rest_apis()", False, "items",None],
	#  ["lambda", "LAMBDA", "list_functions()", False, "Functions",None],
	["cognito-identity", "COGNITO-identity", "list_identity_pools(MaxResults=60)", True, "IdentityPools",None],
	["cognito-idp", "COGNITO-idp", "list_user_pools(MaxResults=60)", True, "UserPools",None],
	["ecs", "ECS", "list_clusters()", False, "clusterArns",None],
	["ecr", "ECR", "describe_repositories()", False, "repositories",None],
	["elb", "ELB", "describe_load_balancers()", False, "LoadBalancerDescriptions",None],
	["elbv2", "ELBv2", "describe_load_balancers()", False, "LoadBalancers",None],
	["elbeanstalk-env", "ELBEANSTALK-env", "describe_environments()", False, "Environments",None],
	["elbeanstalk-app", "ELBEANSTALK-app", "describe_applications()", False, "Applications",None],
	["kms", "KMS", "list_keys()", False, "Keys",None],	
	["rds", "RDS", "describe_db_instances()", False, "DBInstances",None],
	["secretsmanager", "SECRETSMANAGER", "list_secrets()", False, "SecretList",None],
	["sns", "SNS", "list_topics()", False, "Topics",None],
	["cloudfront", "CLOUDFRONT", "list_distributions()", True, "DistributionList","Quantity"],
]  	

def get_service_count(service_name, common_name, region_name, method_to_invoke, is_global, response_1level, response_2level=None):
	client = get_client(service_name,region_name)
	if client == None:
		dict[service_name].update({region_name:"N/A"})
		#dict[service_name]['Global-Total'] += count
	else:		
		try:						
			try:
				response = eval("client." + method_to_invoke)
			except:
				response = eval("client." + method_to_invoke + ".get('ResponseMetadata')")
			
			if response_2level != None:							
				count = response[response_1level][response_2level]
			else:
				count = len(response[response_1level])
			count = random.randint(1, 10)
			logging.debug("Service: %s, Region: %s, Count: %s", common_name, region_name, count)						
			dict[service_name].update({region_name:count})
			dict[service_name]['Global-Total'] += count
			#return count
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logging.debug("Exception: %s, %s, %s", exc_type, exc_obj, exc_tb.tb_lineno)			
			logging.debug("Except. Service: %s, Region: %s, Count: %s", common_name, region_name, 0)
			#return 0		

if __name__ == "__main__":
	threads = list()
	for index, service in enumerate(services):
		logging.debug("Main    : create and start thread %d.", index)		
		dict[service[0]] = {'ServiceName':service[1],'Global-Total':0}		
		for region in allRegions:
			if service[3] == True:
				x = threading.Thread(target=get_service_count, args=(service[0], service[1], "us-east-1", service[2], service[3], service[4], service[5]))				
				threads.append(x)
				x.start()				
				break
			else:
				x = threading.Thread(target=get_service_count, args=(service[0], service[1], region, service[2], service[3], service[4], service[5]))
				threads.append(x)
				x.start()

	for index, thread in enumerate(threads):
		logging.debug("Main    : before joining thread %d.", index)
		thread.join()		
		logging.debug("Main    : thread %d done", index)

with open('output.csv', 'w', newline='') as csvfile:
	fieldnames = ['ServiceName','Global-Total'] + allRegions
	print("Header:", fieldnames)
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	for i in dict:
		print( "Dict[i]:{0} i:{1}".format(dict[i],i) )
		writer.writerow(dict[i])
    
print(dict)


