# handler for ecs run task
import os
import boto3
import shutil
import zipfile

# add ecs run task with boto3

def handler(batchs:list[int]):
    ecs = boto3.client('ecs', region_name='ap-northeast-1')
    for batch_number in batchs:
        print(f"batch_number: {batch_number} is running...")
        ecs.run_task(
            cluster='geniac_takahashi',
            launchType='FARGATE',
            taskDefinition='geniac_takahashi:26',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        'subnet-0e10da10bd1910abd'
                    ],
                    'securityGroups': [
                        'sg-0fc99820582700703'
                    ],
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides={
                'containerOverrides': [
                    {
                        'name': 'app',
                        'command': [
                        'python', 'main.py', str(batch_number)
                        ]
                    },
                ]
            },
            count=1,
        )
        

if __name__ == "__main__":


    # リスト内包表記で作成
    # batchs = [i for i in range(391,400 )]
    batchs = [100,101,102]

    handler(batchs)

