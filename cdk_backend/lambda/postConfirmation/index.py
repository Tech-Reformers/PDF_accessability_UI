import json
import os
import boto3

def handler(event, context):
    print('Post Confirmation Trigger: new user sign-up')
    if event['triggerSource'] != 'PostConfirmation_ConfirmSignUp':
        print(f"Skipping initialization - trigger source is {event['triggerSource']}")
        return event
    
    # Retrieve group names from environment variables
    DEFAULT_GROUP = str(os.environ.get('DEFAULT_GROUP_NAME'))
    AMAZON_GROUP = str(os.environ.get('AMAZON_GROUP_NAME'))
    ADMIN_GROUP = str(os.environ.get('ADMIN_GROUP_NAME'))

    # Define attribute defaults based on group
    group_attributes = {
        DEFAULT_GROUP: {
            'custom:first_sign_in': 'true',
            'custom:total_files_uploaded': '0',
            'custom:max_files_allowed': '8',
            'custom:max_pages_allowed': '10',
            'custom:max_size_allowed_MB': '25'
        },
        AMAZON_GROUP: {
            'custom:first_sign_in': 'true',
            'custom:total_files_uploaded': '0',
            'custom:max_files_allowed': '15',
            'custom:max_pages_allowed': '10',
            'custom:max_size_allowed_MB': '25'
        },
        ADMIN_GROUP: {
            'custom:first_sign_in': 'true',
            'custom:total_files_uploaded': '0',
            'custom:max_files_allowed': '100',
            'custom:max_pages_allowed': '2500',
            'custom:max_size_allowed_MB': '1000'
        }
    }

    try:
        cognito_idp = boto3.client('cognito-idp')
        user_pool_id = event['userPoolId']
        username = event['userName']

        # All new users are assigned to the default group.
        # Admins can promote users to higher groups via the Cognito console,
        # which triggers UpdateAttributesGroups to apply the new group's limits.
        assigned_group = DEFAULT_GROUP

        # Add user to the assigned group
        cognito_idp.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=assigned_group
        )
        print(f'User {username} added to group {assigned_group}.')

        # Initialize custom attributes based on the assigned group
        attributes = group_attributes.get(assigned_group, {})
        user_attributes = [{'Name': key, 'Value': value} for key, value in attributes.items()]

        if user_attributes:
            cognito_idp.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username=username,
                UserAttributes=user_attributes
            )
            print(f'Successfully initialized attributes for group {assigned_group}.')

    except Exception as error:
        print(f'Error in post confirmation trigger: {error}')

    return event
