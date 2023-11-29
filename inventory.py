import boto3
import json
import csv


"""
To run it run AWS CloudShell, upload this file and run it with command: 

python3 inventory.py

Download using CloudShell -> Actions -> Download file ( put: output.csv )
"""

dict = {}

###################### Account ######################

clientAccount = boto3.client('account')
response = clientAccount.list_regions(RegionOptStatusContains=['ENABLED','ENABLED_BY_DEFAULT'])
allRegions = []
for i in response['Regions']:
	allRegions.append(i['RegionName'])

################# S3 ######################

client = boto3.client('s3')
s3namesArr = []
s3regionsArr = []
response = client.list_buckets()
dict['S3'] = [len(response['Buckets'])]
for i in response['Buckets']:
	s3namesArr.append(i['Name'])
for i in s3namesArr:
	location = client.get_bucket_location(Bucket=s3namesArr[i])['LocationConstraint']
	if location == None:
		s3regionsArr.append('us-east-1')
	else:
		s3regionsArr.append(location)

################ Iteration ############################

for iter in range(0, len(allRegions)):	
	client = boto3.client('ec2',region_name=allRegions[iter])			
	response = client.describe_instances()	
	if iter == 0:
		dict['EC2'] = [0]
	dict['EC2'].append(len(response['Reservations']))		
	
	response = client.describe_vpcs()
	if iter == 0:
		dict['VPC'] = [0]
	dict['VPC'].append(len(response['Vpcs']))

	response = client.describe_vpn_connections()
	if iter == 0:
		dict['VPN'] = [0]
	dict['VPN'].append(len(response['VpnConnections']))

	response = client.describe_subnets()
	if iter == 0:
		dict['SUBNETS'] = [0]
	dict['SUBNETS'].append(len(response['Subnets']))

	response = client.describe_security_groups()
	if iter == 0:
		dict['SG'] = [0]
	dict['SG'].append(len(response['SecurityGroups']))

	if iter == 0:
		client = boto3.client('route53')
		response = client.get_hosted_zone_count()
		dict['R53'] = [response['HostedZoneCount']]
	dict['R53'].append(0)

	client = boto3.client('acm',region_name=allRegions[iter])
	response = client.list_certificates()
	if iter == 0:
		dict['ACM'] = [0]
	dict['ACM'].append(len(response['CertificateSummaryList']))	

	client = boto3.client('apigatewayv2',region_name=allRegions[iter])
	response = client.get_apis()
	if iter == 0:
		dict['API_GW_HTTP'] = [0]
	dict['API_GW_HTTP'].append(len(response['Items']))

	client = boto3.client('apigateway',region_name=allRegions[iter])
	response = client.get_rest_apis()
	if iter == 0:
		dict['API_GW_EDGE'] = [0]
	dict['API_GW_EDGE'].append(len(response['items']))

	client = boto3.client('lambda',region_name=allRegions[iter])
	response = client.list_functions()
	if iter == 0:
		dict['LAMBDA'] = [0]
	dict['LAMBDA'].append(len(response['Functions']))

	if iter == 0:
		dict['COGNITO-identity'] = [0]
	
	cognitoRegions = boto3.session.Session().get_available_regions('cognito-identity')
	if allRegions[iter] in cognitoRegions:
		client = boto3.client('cognito-identity',region_name=allRegions[iter])
		response = client.list_identity_pools(MaxResults=60)
		dict['COGNITO-identity'].append(len(response['IdentityPools']))
	else:
		dict['COGNITO-identity'].append('N/A')
	
	if iter == 0:
		dict['COGNITO-idp'] = [0]
	
	cognitoRegions = boto3.session.Session().get_available_regions('cognito-idp')
	if allRegions[iter] in cognitoRegions:
		client = boto3.client('cognito-idp',region_name=allRegions[iter])
		response = client.list_user_pools(MaxResults=60)
		dict['COGNITO-idp'].append(len(response['UserPools']))
	else:
		dict['COGNITO-idp'].append('N/A')

    ################ S3 ######################

	dict['S3'].append(s3regionsArr.count(allRegions[iter]))

	################# CloudWatch ######################


	################# CloudTrail ######################


	################# CloudFormation ######################


	################# CloudFront ######################


	################# Elastic Container Service ######################

	client = boto3.client('ecs',region_name=allRegions[iter])
	response = client.list_clusters()
	if iter == 0:
		dict['ECS'] = [0]
	dict['ECS'].append(len(response['clusterArns']))
	
	client = boto3.client('ecr',region_name=allRegions[iter])
	response = client.describe_repositories()
	if iter == 0:
		dict['ECR'] = [0]
	dict['ECR'].append(len(response['repositories']))
	
	client = boto3.client('elb',region_name=allRegions[iter])
	response = client.describe_load_balancers()
	if iter == 0:
		dict['ELB'] = [0]
	dict['ELB'].append(len(response['LoadBalancerDescriptions']))

	client = boto3.client('elbv2',region_name=allRegions[iter])
	response = client.describe_load_balancers()
	if iter == 0:
		dict['ELBv2'] = [0]
	dict['ELBv2'].append(len(response['LoadBalancers']))

	client = boto3.client('elasticbeanstalk',region_name=allRegions[iter])
	response = client.describe_environments()
	if iter == 0:
		dict['ELBEANSTALK-env'] = [0]
	dict['ELBEANSTALK-env'].append(len(response['Environments']))

	response = client.describe_applications()
	if iter == 0:
		dict['ELBEANSTALK-app'] = [0]
	dict['ELBEANSTALK-app'].append(len(response['Applications']))

	client = boto3.client('kms',region_name=allRegions[iter])
	response = client.list_keys()
	if iter == 0:
		dict['KMS'] = [0]
	dict['KMS'].append(len(response['Keys']))

	client = boto3.client('rds',region_name=allRegions[iter])
	response = client.describe_db_instances()
	if iter == 0:
		dict['RDS'] = [0]
	dict['RDS'].append(len(response['DBInstances']))

	client = boto3.client('secretsmanager',region_name=allRegions[iter])
	response = client.list_secrets()
	if iter == 0:
		dict['SECRETSMANAGER'] = [0]
	dict['SECRETSMANAGER'].append(len(response['SecretList']))

	client = boto3.client('sns',region_name=allRegions[iter])
	response = client.list_subscriptions()
	if iter == 0:
		dict['SNS'] = [0]
	dict['SNS'].append(len(response['Subscriptions']))

	if iter == 0:
		client = boto3.client('cloudfront',region_name='us-east-1')
		response = client.list_distributions()
		dict['CLOUDFRONT'] = [response['DistributionList']['Quantity']]
	dict['CLOUDFRONT'].append(0)

print(dict)

out_filename = "output.csv"

with open(out_filename, "w") as csv_file:
	writer = csv.writer(csv_file)
	
	writer.writerow(["ServiceName","Global"]+allRegions)
	for iter in dict:
		writer.writerow([iter]+dict[iter])
