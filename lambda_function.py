import json
import boto3
import pprint
from kubernetes import client
import base64
import traceback
from os import path

boto3.set_stream_logger('')
CLUSTER_NAME = 'your-cluster'
REGION = 'us-east-1'
eks_api = boto3.client('eks', region_name=REGION)
ssm = boto3.client('ssm', region_name=REGION)


def lambda_handler(event, context):
    try:
        cluster_info = eks_api.describe_cluster(name=CLUSTER_NAME)
        cluster_endpoint = cluster_info['cluster']['endpoint']

        if not path.exists("/tmp/cluster_cert.pem"):
            cluster_cert = cluster_info['cluster']['certificateAuthority']
            cluster_cert_decoded = base64.b64decode(cluster_cert['data'])
            f = open("/tmp/cluster_cert.pem", "wb")
            f.write(cluster_cert_decoded)
            f.close()

        # Get bearer Token from SSM Parameter Store
        bearer_token = ssm.get_parameter(Name='Eksctl-Lambda-SA-Token',
                                         WithDecryption=True)

        configuration = client.Configuration()
        configuration.api_key["authorization"] = bearer_token['Parameter'][
            'Value']
        configuration.api_key_prefix['authorization'] = 'Bearer'
        configuration.host = cluster_endpoint
        configuration.ssl_ca_cert = '/tmp/cluster_cert.pem'

        # Get all the deployments in a specific namespaceq
        apps_v1 = client.AppsV1Api(client.ApiClient(configuration))
        deployment = apps_v1.list_namespaced_deployment(namespace="default",pretty="pretty")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(deployment)
       
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"Status ": "Success"})
        }

    except:
        var = traceback.format_exc()
        print(f"Something went wrong - {var}")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"Status ": "Failure"})
        }