# coding = utf-8
# my_fastapi_app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from aiomysql import Pool, Connection
from data_base.main import get_db_conn
from models.user import User, Login
from ..utils.response import response_result
router = APIRouter()

@router.get('/fast/getUserlist')
async def read_user_list(conn=Depends(get_db_conn)):
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT * FROM my_project.userinfo")
        result = await cursor.fetchall()
        if not result:
            return response_result(code=200, msg='查询成功', operation='查询用户列表')
        data = [{'name': row[1], 'id': row[0], 'username': row[2]} for row in result]
        return response_result(code=200, msg='查询成功', operation='查询用户列表', data=data)

@router.post('/fast/createUser')
async def save_user_info(user_info: User, conn: Connection = Depends(get_db_conn)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(f"SELECT * from my_projct.useringo where username = {user_info.username}")
            result = await cursor.fetchall()
            if not result:
                await cursor.execute("INSERT INTO my_project.userinfo (name, username, password) VALUES (%s, %s, %s)",
                                     (user_info.name, user_info.username, user_info.password))
                return response_result(code=200, msg='用户创建成功', operation='创建用户')
            return response_result(code=1000, msg='用户名存在', operation='创建用户')
    except Exception as e:
        response_result(code=500, msg=str(e), operation='系统错误')
        return { 'state': 500, 'error': str(e) }
        # 如果出现任何异常，例如数据库连接问题或SQL执行问题，将抛出 HTTP 500 内部服务器错误
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/fast/login')
async def user_login(LoginInfo: Login, conn: Connection = Depends(get_db_conn) ):
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT password FROM my_project.userinfo u where username = %s", LoginInfo.username)
        result = await cursor.fetchone()
        if not result:
            return response_result(code=10002, msg='用户不存在', operation='用户登录')
        if result[0] == LoginInfo.password.get_secret_value():
            return response_result(code=200, msg='登录成功', operation='用户登录', userInfo = {"token":'111122'})
        return response_result(code=10001, msg='密码或用户名有误，请检查后重新输入', operation='用户登录')
