import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ShortLinks')
metadata_table = dynamodb.Table('ClickMetadata')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def extract_metadata(headers):
    user_agent = headers.get("User-Agent", "Unknown")
    source_ip = headers.get("X-Forwarded-For", "Unknown").split(",")[0].strip()

    browser = "Unknown"
    if "Firefox" in user_agent:
        browser = "Firefox"
    elif "Chrome" in user_agent:
        browser = "Chrome"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        browser = "Safari"
    elif "Edge" in user_agent:
        browser = "Edge"

    device_type = "Desktop"
    if "Mobile" in user_agent:
        device_type = "Mobile"
    elif "Tablet" in user_agent:
        device_type = "Tablet"

    return {
        'ip_address': source_ip,
        'user_agent': user_agent,
        'browser': browser,
        'device': device_type,
        'timestamp': datetime.utcnow().isoformat()
    }

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    route_key = event['requestContext']['routeKey']
    print("RouteKey:", route_key)

    if route_key.startswith("OPTIONS "):
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': ''
        }

    if route_key == "POST /shorten":
        try:
            body = json.loads(event.get('body') or '{}')
            original_url = body.get('url')
            if not original_url:
                raise ValueError("Missing 'url' in request body")

            short_code = uuid.uuid4().hex[:6]
            table.put_item(Item={
                'short_link': short_code,
                'original_url': original_url,
                'created_at': datetime.utcnow().isoformat(),
                'click_count': 0
            })

            # ✅ Fixed: return the correct domain for redirection
            short_url = f"https://go.bitlink.uk/{short_code}"

            print(f"Created short link {short_code} → {original_url}")
            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({'short_url': short_url})
            }

        except Exception as e:
            print("Error in POST /shorten:", str(e))
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': str(e)})
            }

    if route_key.startswith("GET /clicks/"):
        path_params = event.get('pathParameters') or {}
        short_id = path_params.get('short_id')
        print("Handling GET /clicks/, short_id:", short_id)

        if not short_id:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': "Missing short_id in path"})
            }

        try:
            response = table.get_item(Key={'short_link': short_id})
            item = response.get('Item')
            if not item:
                return {
                    'statusCode': 404,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': "Short URL not found"})
                }

            click_count = int(item.get('click_count', 0))
            metadata_response = metadata_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('short_link').eq(short_id)
            )

            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'short_link': item['short_link'],
                    'original_url': item['original_url'],
                    'click_count': click_count,
                    'created_at': item.get('created_at', 'N/A'),
                    'clicks': metadata_response.get('Items', [])
                })
            }

        except Exception as e:
            print("Error in GET /clicks/:", str(e))
            return {
                'statusCode': 500,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': "Internal Server Error"})
            }

    if route_key.startswith("GET /metadata/"):
        path_params = event.get('pathParameters') or {}
        short_id = path_params.get('short_id')
        print("Handling GET /metadata/, short_id:", short_id)

        if not short_id:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': "Missing short_id in path"})
            }

        try:
            metadata_response = metadata_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('short_link').eq(short_id)
            )

            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps(metadata_response.get('Items', []))
            }

        except Exception as e:
            print("Error fetching metadata:", str(e))
            return {
                'statusCode': 500,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': "Failed to fetch metadata"})
            }

    if route_key.startswith("GET /") and not route_key.startswith("GET /clicks"):
        path_params = event.get('pathParameters') or {}
        short_code = path_params.get('short_code')
        print("Handling GET redirect, short_code:", short_code)

        if not short_code:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': "Missing short_code in path"})
            }

        try:
            response = table.get_item(Key={'short_link': short_code})
            item = response.get('Item')
            if not item:
                return {
                    'statusCode': 404,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': "Short URL not found"})
                }

            try:
                table.update_item(
                    Key={'short_link': short_code},
                    UpdateExpression='ADD click_count :inc',
                    ExpressionAttributeValues={':inc': 1}
                )
            except Exception as e:
                print("Failed to increment click_count:", str(e))

            try:
                metadata = extract_metadata(event.get('headers') or {})
                metadata['short_link'] = short_code
                metadata_table.put_item(Item=metadata)
            except Exception as e:
                print("Metadata logging failed:", str(e))

            return {
                'statusCode': 301,
                'headers': {
                    **CORS_HEADERS,
                    'Location': item['original_url']
                },
                'body': ''
            }

        except Exception as e:
            print("Error in GET redirect:", str(e))
            return {
                'statusCode': 500,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': "Internal Server Error"})
            }

    return {
        'statusCode': 404,
        'headers': CORS_HEADERS,
        'body': json.dumps({'message': 'Not Found'})
    }
