# eks-lambda - Lambda function to query/update your EKS cluster

This example makes use of the Kubernetes Python client - https://github.com/kubernetes-client/python

- Assumes that you have a service account token present as an ancrypted string in Systems Manager Parameter Store
- Modify the function code as needed and run the command to add it to the deployment package
```
zip -g my-deployment-package.zip lambda_function.py
```
- If the function is being created for the first time, use the below command. You would need to have a Lambda execution role in place which has access to eks:DescribeCluster and ssm:GetParameter, in addition to basic lambda execution role permissions.
```
aws lambda create-function --function-name EksLambdaFunction --runtime python3.9 --zip-file fileb://my-deployment-package.zip --role <<lambda-execution-role-arn>> --handler lambda_function.lambda_handler
```

- If you are updating the function code for an existing function, you can use the below command -
```
aws lambda update-function-code --function-name EksLambdaFunction --zip-file fileb://my-deployment-package.zip
```

