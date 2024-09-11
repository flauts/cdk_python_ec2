#!/bin/bash

# Get temporary credentials
CREDENTIALS=$(aws sts assume-role --role-arn arn:aws:iam::172067734210:role/LabRole --role-session-name CDKSession)

# Extract the credentials
export AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDENTIALS | jq -r '.Credentials.SessionToken')

# Set CDK_NEW_BOOTSTRAP to skip bootstrapping
export CDK_NEW_BOOTSTRAP=1

# Synthesize or deploy the CDK stack
cdk bootstrap --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess aws://172067734210/us-east-1  # or 'cdk deploy' if you want to deploy