import requests
from dotenv import load_dotenv
import os
import json
import uuid

def init():
    # load .env
    load_dotenv()

    database_id = os.environ.get('DATABASE_ID')
    token = os.environ.get('TOKEN')

    headers = {
        "Authorization": f"{token}",
        "Notion-Version": "2021-05-11",
        "Content-Type": "application/json"
    }

    return headers, database_id

def build_payload(database_id, username, data, unique_url=''):
    # if unique_url == '':  # 만약 unique_url이 제공되지 않으면 새로운 UUID 생성
    #     unique_url = str(uuid.uuid4())

    payload = {
        "parent": {
            "database_id": database_id
        },
        "properties": {
            "name": {
                "title": [
                    {
                        "text": {
                            "content": username
                        }
                    }
                ]
            },
            "user_id": {
                "rich_text": [
                    {
                        "text": {
                            "content": str(uuid.uuid4())
                        }
                    }
                ]
            },
            "unique_url": {
                "rich_text": [
                    {
                        "text": {
                            "content": unique_url
                        }
                    }
                ]
            },
            "timetable": {
                "rich_text": [
                    {
                        "text": {
                            "content": data
                        }
                    }
                ]
            }
        }}

    return payload, unique_url

def savedb(username, data, id=''):
    # add new username and unique id to notion page
    url = f'https://api.notion.com/v1/pages'
    headers, database_id = init()
    payload, unique_url = build_payload(database_id, username, data, id)

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # 응답 상태코드 확인
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        raise Exception("Failed to save data to Notion")

    return unique_url

def save_db_test(username, data, unique_url=''):
    # Notion API 호출 URL 및 초기화
    url = f'https://api.notion.com/v1/pages'
    headers, database_id = init()

    # Payload 생성 (unique_url을 인자로 받음)
    payload, unique_url = build_payload(database_id, username, data, unique_url)

    # Notion API 호출
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # 응답 상태코드 확인
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        raise Exception("Failed to save data to Notion")

    return unique_url

async def filter_meet(id):
    headers, database_id = init()
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "filter": {
            "property": "unique_url",
            "rich_text": {
                "equals": id
            }
        }
    }
    res = requests.post(url, json=payload, headers=headers)

    meet = {}
    for person in res.json()["results"]:
        key = person["properties"]["name"]["title"][0]["plain_text"]
        value = json.loads(person["properties"]["timetable"]["rich_text"][0]["plain_text"])
        meet[key] = value

    return meet


# 새로운 메서드 추가: username으로 페이지 찾기
def find_page_by_username(username):
    headers, database_id = init()
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "filter": {
            "property": "name",
            "title": {
                "equals": username
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            # 페이지가 있으면 첫 번째 페이지의 ID 반환
            return results[0]['id']
    return None


def update_page_with_code(page_id, entrance_code):
    # 먼저 해당 페이지의 데이터를 가져오기
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers, _ = init()

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        page_data = response.json()

        # properties에서 unique_url을 가져옵니다.
        unique_url_property = page_data["properties"].get("unique_url", None)

        # 만약 unique_url이 없다면 빈 문자열로 초기화
        if unique_url_property is None or not unique_url_property.get("text"):
            existing_unique_urls = ""
        else:
            # 기존 unique_url을 가져와 쉼표로 구분된 문자열로 처리
            existing_unique_urls = unique_url_property.get("text", [{}])[0].get('plain_text', "")

        # 새로운 entrance_code를 쉼표로 구분하여 추가
        if existing_unique_urls:
            updated_unique_urls = existing_unique_urls + "," + entrance_code
        else:
            updated_unique_urls = entrance_code

        # updated payload
        payload = {
            "properties": {
                "unique_url": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": updated_unique_urls,  # 업데이트된 unique_url
                                "plain_text": updated_unique_urls  # plain_text 필드를 사용하여 구분
                            },
                            "annotations": {"bold": False, "italic": False, "strikethrough": False}
                        }
                    ]
                }
            }
        }

        # 페이지 업데이트
        update_response = requests.patch(url, headers=headers, json=payload)

        # 페이지 업데이트 상태 로그
        if update_response.status_code == 200:
            print("Page successfully updated.")
        else:
            print(f"Failed to update page. Status code: {update_response.status_code}")

        return update_response.status_code == 200

    else:
        print(f"Failed to fetch page data. Status code: {response.status_code}")
        return False