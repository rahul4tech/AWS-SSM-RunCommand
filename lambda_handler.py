import json
import boto3

def lambda_handler(event, context):
    ssm_client = boto3.client('ssm')
    
    # Replace 'your-instance-id' with the actual instance ID
    instance_id = 'ec2_instance_id_will_go_her'
    
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands': [
                'cd /root',
                'sh test.sh'
            ]
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Command sent to EC2 instance')
    }

