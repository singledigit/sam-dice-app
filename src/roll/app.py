import json
import random
import os
import boto3
import datetime
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key

logger = Logger()
table = boto3.resource('dynamodb').Table(os.environ["DICE_TABLE"])

def get_response(event):
    return {
        "statusCode": 200,
        "body": json.dumps(query_last_10_rols_from_table(event["queryStringParameters"]["name"])["Items"], default=str)
    }

def query_last_10_rols_from_table(name):
    response = table.query(
        Limit=10,
        KeyConditionExpression=Key('name').eq(name))
    return response

def post_response(event):
    if generate_error():
        logger.info({"operation": "simulated error generated"})
        return {
            "statusCode": 500,
        }
    
    parsedBody = json.loads(event["body"])
    print(parsedBody)
    roll = roll_dice()
    logger.info({"operation": "dice roll", "diceRoll": roll})

    save_data_to_dynamodb_table(parsedBody["name"], roll)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "diceRoll": roll
        }),
    }

def roll_dice():
    return random.randint(1, 6)

def save_data_to_dynamodb_table(name, roll):
    table.put_item(Item={
        "name": name,
        "createdAt": datetime.datetime.now().isoformat(),
        "roll": roll
    })

def generate_error():
    if random.randint(1, 100) <= int(os.environ["CHANCE_OF_FAILURE"]):
        return True
    return False

def lambda_handler(event, context):
    if event["httpMethod"] == "POST":
        return post_response(event)
    else:
        return get_response(event)
