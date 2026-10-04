import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('InventoryTable')

# Helper class to convert Decimal objects to float/int for JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert float/int dynamically
            return float(obj) if obj % 1 != 0 else int(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    http_method = event.get('httpMethod', '')
    
    try:
        # GET ALL ITEMS OR SPECIFIC ITEM
        if http_method == 'GET':
            params = event.get('queryStringParameters')
            if params and 'itemId' in params:
                response = table.get_item(Key={'itemId': params['itemId']})
                item = response.get('Item', {})
                return build_response(200, item)
            else:
                response = table.scan()
                return build_response(200, response.get('Items', []))
                
        # ADD OR UPDATE ITEM
        elif http_method == 'POST':
            body = json.loads(event.get('body', '{}'), parse_float=Decimal)
            table.put_item(Item=body)
            return build_response(201, {'message': 'Item saved successfully', 'item': body})
            
        else:
            return build_response(400, {'message': 'Unsupported HTTP method'})
            
    except Exception as e:
        return build_response(500, {'error': str(e)})

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # Enables CORS
        },
        # Uses DecimalEncoder to safely stringify DynamoDB numbers
        'body': json.dumps(body, cls=DecimalEncoder)
    }
