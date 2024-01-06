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
services = [	
	# ["ec2", "EC2-Instances", "describe_instances()", False, "Reservations",None,{}],
	# ["s3", "S3", "list_buckets()", False, "Buckets",None,{}],
	# ["ec2", "EC2-VPC", "describe_vpcs()", False, "Vpcs",None,{}],
	# ["ec2", "EC2-VPN", "describe_vpn_connections()", False, "VpnConnections",None,{}],
	# ["ec2", "EC2-SUBNETS", "describe_subnets()", False, "Subnets",None,{}],
	# ["ec2", "EC2-SG", "describe_security_groups()", False, "SecurityGroups",None,{}],
	# ["r53", "R53", "get_hosted_zone_count()", True, "HostedZoneCount",None,{}],
	# ["acm", "ACM", "list_certificates()", False, "CertificateSummaryList",None,{}],
	# ["apigatewayv2", "API_GW_HTTP", "get_apis()", False, "Items",None,{}],
	# ["apigateway", "API_GW_EDGE", "get_rest_apis()", False, "items",None,{}],
	["lambda", "LAMBDA", "list_functions()", False, "Functions",None,{}],
	["cognito-identity", "COGNITO-identity", "list_identity_pools(MaxResults=60)", False, "IdentityPools",None, {"next_token_name":"NextToken"}],
	["cognito-idp", "COGNITO-idp", "list_user_pools(MaxResults=60)", False, "UserPools",None,{}],
	# ["ecs", "ECS", "list_clusters()", False, "clusterArns",None,{}],
	# ["ecr", "ECR", "describe_repositories()", False, "repositories",None,{}],
	# ["elb", "ELB", "describe_load_balancers()", False, "LoadBalancerDescriptions",None,{}],
	# ["elbv2", "ELBv2", "describe_load_balancers()", False, "LoadBalancers",None,{}],
	# ["elasticbeanstalk", "ELBEANSTALK-env", "describe_environments()", False, "Environments",None,{}],
	# ["elasticbeanstalk", "ELBEANSTALK-app", "describe_applications()", False, "Applications",None,{}],
	# ["kms", "KMS", "list_keys()", False, "Keys",None,{}],	
	# ["rds", "RDS", "describe_db_instances()", False, "DBInstances",None,{}],
	# ["secretsmanager", "SECRETSMANAGER", "list_secrets()", False, "SecretList",None,{}],
	# ["sns", "SNS", "list_topics()", False, "Topics",None,{}],
	# ["cloudfront", "CLOUDFRONT", "list_distributions()", True, "DistributionList","Quantity",{}],
]  	

def get_service_count(service_name, common_name, region_name, method_to_invoke, is_global, response_1level, response_2level=None, args=None):
	client = get_client(service_name,region_name)
	logging.info("Processing Service: %s, Region: %s", common_name, region_name)
	if client == None:
		dict[common_name].update({region_name:"N/A"})		
	# response = client.get_servers()
	# results = response["serverList"]
	# while "NextToken" in response:
    # response = client.get_servers(NextToken=response["NextToken"])
    # results.extend(response["serverList"]) # 4 na 5
	else:										
		try:			
			response = eval("client." + method_to_invoke)
			if response_2level != None:
				count 	= response[response_1level][response_2level] # no need to paginate				
			else:
				results = response[response_1level]
				if "next_token_name" in args:
					next_token_name = args['next_token_name']
					method_to_invoke = method_to_invoke[:-1] + "," + next_token_name + "=" + "response['"+next_token_name+"'])"
					while args['next_token_name'] in response:
						response = eval("client." + method_to_invoke)
						results.extend(response[response_1level])
				count = len(results)
		except:
			response = eval("client." + method_to_invoke + ".get('ResponseMetadata')")

		try:
			count = random.randint(1, 10)
			logging.debug("Service: %s, Region: %s, Count: %s", common_name, region_name, count)						
			dict[common_name].update({region_name:count})
			dict[common_name]['Global-Total'] += count			
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logging.debug("Exception: %s, %s, %s", exc_type, exc_obj, exc_tb.tb_lineno)			
			logging.debug("Except. Service: %s, Region: %s, Count: %s", common_name, region_name, 0)			

def get_s3_count(service_name,common_name,region_name): # this needs to be treated differently
	client = get_client(service_name,'us-east-1')
	if client == None:
		dict[common_name].update({region_name:"N/A"})		
	
	names = []
	response = client.list_buckets()		
	
	for i in response['Buckets']:
		names.append(i['Name'])

	for i in names:
		location = client.get_bucket_location(Bucket=i)['LocationConstraint']
		if location == None:
			if dict[common_name].get('us-east-1') == None:
				dict[common_name].update({'us-east-1':1})			
			else:
				dict[common_name].update({'us-east-1':dict[common_name].get('us-east-1')+1})
		else:
			if dict[common_name].get(location) == None:
				dict[common_name].update({location:1})
			else:
				dict[common_name].update({location:dict[common_name].get(location)+1})			
		dict[common_name]['Global-Total'] += 1

if __name__ == "__main__":
	threads = list()
	for index, service in enumerate(services):
		logging.debug("Main    : create and start thread %d.", index)		
		dict[service[1]] = {'ServiceName':service[1],'Global-Total':0}		
		
		if service[0] == "s3":
			get_s3_count(service_name=service[0],common_name=service[1],region_name="us-east-1")
			continue

		for region in allRegions:
			if service[3] == True: # One pass for global services
				#dict_arg = service[6]
				x = threading.Thread(target=get_service_count, args=(service[0], service[1], "us-east-1", service[2], service[3], service[4], service[5], service[6]) )				   
				threads.append(x)
				x.start()				
				break
			else:
				x = threading.Thread(target=get_service_count, args=(service[0], service[1], region, service[2], service[3], service[4], service[5], service[6]))
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


