import json
import requests
import uvicorn
import numpy as np

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image

# custom module
import exportImg, convertImgFormat, databaseModule, management

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"Server Working"}


# 처음 올릴 경우 - 가능한 시간대 + unique_url 리턴하면 됨.
@app.post("/uploadfile")
async def create_meet(file_url: str, username: str = ''):
    # URL로부터 이미지 다운로드
    response = requests.get(file_url)

    if response.status_code == 200:
        # 이미지 다운로드 성공
        # BytesIO 객체를 사용하여 이미지를 열기
        image = Image.open(BytesIO(response.content))

        # 이미지를 numpy array로 변환
        image_array = np.array(image)

        # 유저의 시간표 read
        timetable = exportImg.export_img(image_array)

        # 유저의 시간표 db에 저장
        unique_url = databaseModule.save_db_test(username, json.dumps(timetable, ensure_ascii=False))

        # 가능한 시간 찾기 함수
        output = management.first_person(timetable)

        return {"user_name": username, "output": output, "unique_url": unique_url}
    else:
        # 이미지 다운로드 실패 시 처리
        return {"error": "Failed to download image from URL."}


# unique id로 get 요청 - 해당 url에 속하는 사람들의 교집합 return
# @app.post("/meet")
# async def add_timetable(id: str = '', file: UploadFile = File(...), username: str = ''):
#     # 존재하는 url인지부터 확인
#     meets = await databaseModule.filter_meet(id)
#
#     if not meets:
#         return {"error": "해당하는 url이 존재하지 않습니다."}
#     else:
#         # 유저의 시간표 read
#         image = convertImgFormat.load_image_into_numpy_array(await file.read())
#         timetable = exportImg.export_img(image)
#
#         # 유저의 시간표 받은 id에 해당하는 url로 db에 저장
#         databaseModule.savedb(username, json.dumps(timetable, ensure_ascii=False), id)
#
#         # 겹치는 meet 가져오기
#         meets = await databaseModule.filter_meet(id)
#
#         # 겹치는 시간대 전부 표시하는 알고리즘
#         res = management.filter_table(meets)
#
#         # return res
#         return {"meets": res}


# unique id로 get 요청 - 해당 url에 속하는 사람들의 교집합 return
@app.get("/meeting")
async def filter_timetable(entrance_code: str = ''):
    # 입력값 검증
    if not entrance_code:
        raise HTTPException(status_code=400, detail="Entrance code is required.")

    try:
        # 겹치는 meet 가져오기
        meets = await databaseModule.filter_meet(entrance_code)

        # 겹치는 시간대 전부 표시하는 알고리즘
        res, participants, minimum = management.filter_table(meets)

        return {"meets": res, "participants": participants, "absent": minimum}

    except KeyError:
        raise HTTPException(status_code=404, detail="해당하는 URL이 존재하지 않습니다.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/entrance-codes")
async def save_code(entrance_code: str, user_id: int):
    username = str(user_id)

    # username으로 매칭되는 Notion 페이지를 검색
    page_id = databaseModule.find_page_by_username(username)

    if not page_id:
        raise HTTPException(status_code=404, detail="Page not found for the user")

    # Notion 페이지에 entranceCode 저장
    success = databaseModule.update_page_with_code(page_id, entrance_code)

    if success:
        return {"entrance_code": entrance_code, "user_id": username}
    else:
        raise HTTPException(status_code=500, detail="Failed to save the entrance code.")

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
