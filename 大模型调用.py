import requests

def api调用(问题):
    url = 'http://localhost:11434/api/generate'
    payload = {
        'model': 'gemma:7b',
        'prompt': 问题,
        'stream': False
    }

    try:
        # 发送POST请求
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 如果响应不为 200，则抛出异常

        data = response.json()
        model_name = data['model']
        created_at = data['created_at']
        回答 = data['response']
        print(model_name)
        print(created_at)
        print(回答)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

api调用(input())