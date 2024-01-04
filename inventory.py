import boto3
import json
import csv
import logging
import threading
import time
import random

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
	# ["apigw_http", "API_GW_HTTP", "get_apis()", False, "Items"],
	# ["apigw_edge", "API_GW_EDGE", "get_rest_apis()", False, "items"],
	# ["lambda", "LAMBDA", "list_functions()", False, "Functions"],
	# ["cognito-identity", "COGNITO-identity", "list_identity_pools(MaxResults=60)", True, "IdentityPools"],
	# ["cognito-idp", "COGNITO-idp", "list_user_pools(MaxResults=60)", True, "UserPools"],
	# ["ecs", "ECS", "list_clusters()", False, "clusterArns"],
	# ["ecr", "ECR", "describe_repositories()", False, "repositories"],
	# ["elb", "ELB", "describe_load_balancers()", False, "LoadBalancerDescriptions"],
	# ["elbv2", "ELBv2", "describe_load_balancers()", False, "LoadBalancers"],
	# ["elbeanstalk-env", "ELBEANSTALK-env", "describe_environments()", False, "Environments"],
	# ["elbeanstalk-app", "ELBEANSTALK-app", "describe_applications()", False, "Applications"],
	# ["kms", "KMS", "list_keys()", False, "Keys"],	
	# ["rds", "RDS", "describe_db_instances()", False, "DBInstances"],
	# ["secretsmanager", "SECRETSMANAGER", "list_secrets()", False, "SecretList"],
	# ["sns", "SNS", "list_topics()", False, "Topics"],
	["cloudfront", "CLOUDFRONT", "list_distributions()", True, "DistributionList][Quantity]"],
]  	

def get_service_count(service_name, common_name, region_name, method_to_invoke, is_global, response_name):
	client = get_client(service_name,region_name)
	if client == None:
		return 0
	else:
		#if is_global:
		#	client = get_client(service_name, "us-east-1")
		try:						
			try:
				response = eval("client." + method_to_invoke)
			except:
				response = eval("client." + method_to_invoke + ".get('ResponseMetadata')")			
			
			if response_name in response:
				count = len(response[response_name])
			else:
				count = response[response_name]
			logging.info("Service: %s, Region: %s, Count: %s", common_name, region_name, count)
			dict[common_name] = {region_name: count}
			return count
		except:
			logging.info("Service: %s, Region: %s, Count: %s", common_name, region_name, 0)
			return 0		

if __name__ == "__main__":
	threads = list()
	for index, service in enumerate(services):
		logging.info("Main    : create and start thread %d.", index)		
		for region in allRegions:
			if service[3] == True:
				x = threading.Thread(target=get_service_count, args=(service[0], service[1], "us-east-1", service[2], service[3], service[4]))				
				threads.append(x)
				x.start()
				break
			else:
				x = threading.Thread(target=get_service_count, args=(service[0], service[1], region, service[2], service[3], service[4]))
				threads.append(x)
				x.start()

	for index, thread in enumerate(threads):
		logging.info("Main    : before joining thread %d.", index)
		thread.join()
		logging.info("Main    : thread %d done", index)

print(dict)
