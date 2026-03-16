"""
API端点工具函数 - 添加超时控制
"""
import asyncio
from functools import wraps
from fastapi import HTTPException

def timeout_handler(seconds=5):
    """API超时装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise HTTPException(status_code=408, detail=f"请求超时（{seconds}秒）")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
        return wrapper
    return decorator

def safe_api_call(func):
    """安全的API调用装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except HTTPException:
            raise
        except Exception as e:
            print(f"API错误 [{func.__name__}]: {e}")
            raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
    return wrapper
