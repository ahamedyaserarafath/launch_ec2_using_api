# Launching the EC2 Instance using native AWS API. 
- [Introduction](#Introduction)
- [Pre-requisites](#pre-requisites)
- [Steps to run script](#Steps-to-run-script)

# Introduction
In this repo, we are lanuch ec2 instance using native AWS API

# Pre-requisites 
* Ensure you install the latest version of python and requests package.
```
pip install requests
```

# Steps to run script
* We need IAM user access key and secert key to run this script. Please refer AWS documents to create the same and that particular user need to have access to create the ec2 instance.

```
./awsapi_createinstance.py -k <AWS_ACCESS_KEY> -s <AWS_SECRET_KEY> --aws_region <AWS_REGION> -t <AWS_INSTANCE_TYPE>
```
```
./awsapi_createinstance.py -k ABCDEFGH -s QWERTYUIASDFGHJWERTYUSDFGH --aws_region us-east-1 -t t2.micro

```

