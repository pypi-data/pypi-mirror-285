import base64
import hashlib
import asyncio
import aiofiles


def async_open(encoding: str = "utf-8", *args, **kwargs):
    async def open(*args, **kwargs):
        async with aiofiles.open(*args, **kwargs) as f:
            return await f.read()

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(open(*args, **kwargs)).decode(encoding=encoding)


def base64_encode(data: str, encoding: str = "utf-8") -> str:
    return base64.b64encode(data.encode(encoding=encoding)).decode(encoding=encoding)


def base64_decode(code: str, encoding: str = "utf-8") -> str:
    return base64.b64decode(code).decode(encoding=encoding)


def md5_encode(data: str, encoding: str = "utf-8") -> str:
    md5 = hashlib.md5()
    md5.update(data.encode(encoding=encoding))
    return md5.hexdigest()


def sha256_encode(data: str, encoding: str = "utf-8") -> str:
    sha256 = hashlib.sha256()
    sha256.update(data.encode(encoding=encoding))
    return sha256.hexdigest()


if __name__ == '__main__':
    data = async_open(file="../../../config/config.ini", mode="rb", encoding="utf-8")
    code = base64_encode(data)
    print(base64_decode(code))
    print(md5_encode(code))
    print(sha256_encode(code))
