import json
import logging


def run(mode, prompt, enable_sampling):
    if mode == "workflow":
        from sre_example.workflow_mode import main
        return main(prompt=prompt, enable_sampling=enable_sampling)
    elif mode == "llm":
        from sre_example.llm_mode import main
        return main(prompt=prompt, enable_sampling=enable_sampling)
    else:
        raise ValueError(f"Unsupported mode: {mode}")


logging.basicConfig(level=logging.INFO)


def handler(event, context):
    logging.info(f"received new request, event content: {event}")
    try:
        body = json.loads(event['body'])
        data = body['data']
        print(f"\n\n!!!!!!type:{type(data)} \n  !!!!!data:{data}\n\n")
        if 'prompt' in data:
            prompt = data['prompt']
        else:
            raise ValueError("prompt is required")
        if 'enable_sampling' in data:
            enable_sampling = data['enable_sampling']
        else:
            enable_sampling = False
        if 'mode' in data:
            mode = data['mode']
        else:
            mode = "workflow"
    except Exception as e:
        logging.error(f"Error parsing request data: {e}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Invalid request body'
            })
        }
    try:
        output_message = run(mode=mode, prompt=prompt, enable_sampling=enable_sampling)
        result = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': "\n".join(output_message)
            })
        }
        return result

    except Exception as e:
        logging.error(f"Error running agent: {e}")
        return {
           'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
               'message': 'Internal server error'
            })
        }