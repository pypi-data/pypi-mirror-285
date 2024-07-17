# 返回fastapi接口基础模板
fastapi_template = """
from fastapi import FastAPI, Request, HTTPException, Response, Header, Depends
import uvicorn

interview_apis = ["/api"]

app = FastAPI(docs_url=None)  # 线上环境禁用/docs接口

# 中间件函数;限制此项目只能访问["/api"]接口
@app.middleware("http")
async def intercept_requests(request: Request, call_next):
    # 获取请求的路径
    path = request.url.path
    # 如果请求的路径是/api则放行请求
    if path in interview_apis:
        response = await call_next(request)
        return response
    # 其他路径全部拒绝
    else:
        return Response(status_code=403, content="Forbidden")

async def validate_token(token: str = Header(...)):
    # token用于声明一个名为token的参数，它的类型为字符串，并且默认值是通过请求头传递的值
    if token != "nV4vzTotGdkqjqgx":
        raise HTTPException(status_code=403, detail="Forbidden")

@app.get('/api', summary='测试接口', description='测试接口')
async def test(token_validation: None = Depends(validate_token)):
    return {"code": 200, "msg": "success"}

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=80, reload=True)
"""