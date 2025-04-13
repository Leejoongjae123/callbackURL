import time
import json
import urllib.request
import urllib.error
import aiohttp
from fastapi import FastAPI, HTTPException, Request
from mangum import Mangum
import asyncio

app = FastAPI()
handler = Mangum(app)

async def send_callback_response(callback_url, response_body):
    """
    콜백 URL로 응답을 전송합니다.
    
    Args:
        callback_url (str): 카카오에서 제공한 콜백 URL
        response_body (dict): 전송할 응답 데이터
    """
    try:
        print(f"콜백 응답 전송 시작: {callback_url}")
        print(f"응답 데이터: {json.dumps(response_body, ensure_ascii=False)[:200]}...")
        
        # 콜백 응답 형식 준수 - useCallback을 true로 설정하고 template 대신 data 사용
        response_data = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": response_body.get("text", "응답이 준비되었습니다.")
                        }
                    }
                ]
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
        }
        print("response_body:", response_data)
        async with aiohttp.ClientSession() as session:
            async with session.post(callback_url, json=response_data, headers=headers) as resp:
                if resp.status == 200:
                    print(f"콜백 응답 전송 성공: {callback_url}")
                    response_text = await resp.text()
                    print(f"콜백 응답: {response_text}")
                else:
                    response_text = await resp.text()
                    print(f"콜백 응답 전송 실패: {resp.status}, {response_text}")
    except Exception as e:
        print(f"콜백 응답 전송 중 오류 발생: {e}")

# 지연된 응답을 처리하는 비동기 함수
async def process_delayed_response(callback_url, response_body, delay_seconds=7):
    """
    지연된 응답을 처리하는 비동기 함수
    
    Args:
        callback_url (str): 카카오에서 제공한 콜백 URL
        response_body (dict): 전송할 응답 데이터
        delay_seconds (int): 지연 시간(초)
    """
    try:
        # 비동기 방식으로 대기
        print("지연 응답 시작")
        await asyncio.sleep(delay_seconds)
        # 콜백 URL로 응답 전송
        print("지연 응답 완료")
        
        # 카카오 챗봇 콜백 응답 형식에 맞게 수정
        callback_response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": response_body.get("text", "응답이 준비되었습니다.")
                        }
                    }
                ]
            }
        }
        
        await send_callback_response(callback_url, response_body)
        print(f"{delay_seconds}초 후 콜백 응답 전송 완료")
    except Exception as e:
        print(f"지연 응답 처리 중 오류 발생: {e}")

@app.post("/sayHello")
async def say_hello(request: Request):
    # 요청 본문 파싱
    request_data = await request.json()
    
    # 카카오 callback URL 가져오기
    callback_url = request_data.get("userRequest", {}).get("callbackUrl", "")
    print('callback_url:', callback_url)
    
    # Authorization 헤더 확인 (디버깅 용도)
    auth_header = request.headers.get("Authorization", "")
    print(f"받은 Authorization 헤더: {auth_header}")
    
    #====질문이 ㅎㅇ면 5초 뒤 답변
    if request_data["userRequest"]["utterance"] == "ㅎㅇ":
        # 나중에 보낼 응답 데이터
        
        
        # 즉시 응답 반환 (useCallback 필수)
        temp_response = {
            "version": "2.0",
            "useCallback": True,
            "data": {
                "text": "생각하고 있는 중이에요😘 \n7초 정도 소요될 거 같아요 기다려 주실래요?!"
            }
        }

        delayed_response = {
            "text": "그건 너무 어려워요 ㅠ_ㅠㅠ"
        }
        
        # 콜백 URL이 있으면 비동기로 응답 전송 (나중에 처리)
        if callback_url:
            print("콜백 URL 있음")
            # 비동기 태스크 생성 - 이벤트 루프를 차단하지 않음
            try:
                # 디버깅을 위한 로그 추가
                print("지연 응답 태스크 생성 시도...")
                task = asyncio.create_task(process_delayed_response(callback_url, delayed_response, 7))
                print(f"비동기 지연 응답 태스크 생성됨: {task}")
            except Exception as e:
                print(f"태스크 생성 중 오류 발생: {e}")
            
        return temp_response
        
    #====질문이 ㅎㅇ가 아니면 일반적인 답변
    response_body = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text":"내용을 전송하였습니다."
                    }
                }
            ]
        }
    }

    return response_body


    
