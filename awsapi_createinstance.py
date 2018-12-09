#!/usr/bin/python
# Note : Above path should be changed if python package location is changes
##******************************************************************************
##
## AWS Create Instance Using API 
##   - Create the Single EC2 instance using aws api 
##   - AWS secert Key, AWS access key, instance type,
##	 aws region as input to create the ec2 instance
##
## V 1.0 / 8 Aug 2017 / Ahamed Yaser Arafath / ahamedyaserarafath@gmail.com
##
##******************************************************************************

#Import respective package which is needed 
import sys, os, base64, datetime, hashlib, hmac 
import argparse
import requests # pip install requests
requests.packages.urllib3.disable_warnings()
import xml.etree.ElementTree as ET

# Global Variable
method = 'POST'
service = 'ec2'
host = 'ec2.amazonaws.com'
url = 'https://ec2.amazonaws.com'
url_parameters = 'Action=RunInstances'
ImageId="ami-a4c7edb2"
MinCount="1"
MaxCount="1"
Version="2016-11-15"
content_type = 'application/x-www-form-urlencoded'
request_data = ""
# Create a date for headers and the credential string
t = datetime.datetime.utcnow()
amz_date = t.strftime('%Y%m%dT%H%M%SZ')
date_stamp = t.strftime('%Y%m%d')
algorithm = 'AWS4-HMAC-SHA256'


def inputArgument():
	'''
	Input arugment function will define what are inputs needed for the scripts
	'''
	try:
		parser=argparse.ArgumentParser(description = 'Script will be responsible for creating the aws ec2 instance using api')
		parser.add_argument('-k', '--aws_access_key', help = 'AWS access key of IAM user')
		parser.add_argument('-s', '--aws_secret_key', help = 'AWS secert key of IAM user')
		parser.add_argument('-r', '--aws_region', help = 'AWS region where we want to launch ec2 instance')
		parser.add_argument('-t', '--aws_instance_type', help = 'AWS instance type like t2.micro, t1.micro..Please refer AWS document')
		arg = parser.parse_args()
		aws_access_key = arg.aws_access_key
		aws_secret_key = arg.aws_secret_key
		aws_region = arg.aws_region
		aws_instance_type = arg.aws_instance_type
		if arg.aws_access_key is None or \
			arg.aws_secret_key is None or \
			arg.aws_region is None or \
			arg.aws_instance_type is None:
			print "Please have a valid input, please look for help"
			sys.exit(1)
		return aws_access_key, aws_secret_key, aws_region, aws_instance_type
	except Exception as e:
		print "Exception while paring input arguments, Exception for your reference : " + str(e)
		sys.exit(1)

def sign(key, msg):
	return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def getSignatureKey(key, date_stamp, regionName, serviceName):
	kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
	kRegion = sign(kDate, regionName)
	kService = sign(kRegion, serviceName)
	kSigning = sign(kService, 'aws4_request')
	return kSigning

def createAuthorizationHeader(url_parameters, content_type, host, \
				amz_date, request_parameters, \
				method, date_stamp, region, \
				service, algorithm,\
				secret_key, access_key):
	'''
	Create the authorization header with the sha256 signature
	which will be generated w.r.t to secert key of IAM user.
	'''
	canonical_uri = '/'
	canonical_querystring = url_parameters
	canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n'
	signed_headers = 'content-type;host;x-amz-date'
	payload_hash = hashlib.sha256(request_parameters).hexdigest()
	canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
	credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
	string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request).hexdigest()
	signing_key = getSignatureKey(secret_key, date_stamp, region, service)
	signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
	authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
	headers = {'content-type':content_type,
			'x-amz-date':amz_date,
			'Authorization':authorization_header}

	return headers

def createInstanceUsingAPI(url, querystring,data,headers):
	'''
	Function will create the ec2 instance using the AWS api
	 with respective data in urlencoded format
	 and with respective authorization header
	'''
	try :
		request_url = url + '?' + querystring
		r = requests.post(request_url, data=data, headers=headers)
		print 'Response code: %d\n' % r.status_code
		response_result = ET.fromstring(r.text)
		xmlns_value = (response_result.tag).split("}")[0] + "}"
		response_instancesSet = response_result.find(xmlns_value + 'instancesSet')
		response_item = response_instancesSet.find(xmlns_value + 'item')
		print "Instance ID : " + response_item.find(xmlns_value + 'instanceId').text
		print "Instance Launch Time : " + response_item.find(xmlns_value + 'launchTime').text
	except requests.exceptions.Timeout as e:
		print("HTTP Timeout Error Accessing "+request_url)
	except requests.exceptions.ConnectionError as e:
		print("HTTP Connection Error Accessing "+request_url)
	except Exception as e:
		print("Generic Exception "+str(e))

if __name__ == '__main__':
	aws_access_key, aws_secret_key, aws_region, aws_instance_type = inputArgument()
	querystring = 'Action=RunInstances'+\
				'&ImageId=' + ImageId + \
				'&InstanceType=' + aws_instance_type + \
				'&MaxCount=' + MaxCount + \
				'&MinCount=' + MinCount + \
				'&Version=' + Version 
	request_headers = createAuthorizationHeader(querystring, content_type, host, \
				amz_date, request_data, \
				method, date_stamp, aws_region, \
				service, algorithm,
				aws_secret_key, aws_access_key)
	createInstanceUsingAPI(url, querystring,request_data,request_headers)
	