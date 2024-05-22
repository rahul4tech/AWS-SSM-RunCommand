import boto3
import time
import json

def run_script_on_ec2(instance_id, script_commands):
    ssm_client = boto3.client('ssm')

    # Start the EC2 instance
    ec2_client.start_instances(InstanceIds=[instance_id])
    
    # Wait for the instance to be in the running state
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    # Additional wait time to ensure the instance is fully initialized
    time.sleep(60)  # Wait for 60 seconds

    # Send the script commands to the instance and run it
    try:
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': script_commands},
            TimeoutSeconds=3600  # Adjust timeout as necessary
        )
        command_id = response['Command']['CommandId']

        # Wait for the command to finish and get the output
        while True:
            time.sleep(10)  # Wait for 10 seconds before checking the command status again
            result = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            if result['Status'] in ['Success', 'Failed', 'TimedOut', 'Cancelled']:
                break

        # Capture the command output and status
        command_output = result.get('StandardOutputContent', '')
        command_error = result.get('StandardErrorContent', '')
        command_status = result.get('Status', '')

        if command_status == 'Success':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': command_status,
                    'output': command_output
                })
            }
        else:
            # Raise an exception with detailed JSON output
            raise Exception(json.dumps({
                'status': command_status,
                'output': command_output,
                'error': command_error
            }))

    except Exception as e:
        # Re-raise the exception to ensure Glue job fails
        raise Exception(f"Error sending command: {str(e)}")

# Example usage
instance_id = 'i-some_EC2_INSTANCE_ID'  # Replace with your EC2 instance ID
script_commands = [
    'cd /home/ec2-user',
    'sh testssm.sh'  # Intentionally incorrect to simulate failure
]

output = run_script_on_ec2(instance_id, script_commands)
print(output)
