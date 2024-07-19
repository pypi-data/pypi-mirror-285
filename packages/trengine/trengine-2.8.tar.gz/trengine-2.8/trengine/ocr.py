import asyncio
import aiohttp
import json
import os


from .exceptions import ApiException


class OCR:
    @staticmethod
    def from_image(path: str, language: str = "eng") -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(AsyncOCR.from_image(path, language))


class AsyncOCR:
    @staticmethod
    async def from_image(path: str, language: str = "eng") -> str:
        with open(path, "rb") as f:
            b = f.read()
        async with aiohttp.ClientSession(
            headers={"Apikey": "donotstealthiskey_ip1"}
        ) as session:
            payload = {
                "language": language,
                "isOverlayRequired": True,
                "OCREngine": 1,
                "detectCheckbox": False,
                "IsCreateSearchablePDF": False,
                "isSearchablePdfHideTextLayer": True,
                "FileType": ".AUTO",
            }
            data = aiohttp.formdata.FormData(quote_fields=False)
            for k, v in payload.items():
                data.add_field(k, str(v))
            data.add_field("file", b, filename=os.path.basename(path))
            async with session.post(
                "https://api8.ocr.space/parse/image", data=data
            ) as response:
                try:
                    result = await response.json()
                except Exception as e:
                    raise BaseException(str(e))

                if isinstance(result, str):
                    raise ApiException(result)
                if not result.get("ParsedResults"):
                    raise ApiException(json.dumps(result, indent=4, ensure_ascii=False))

                return result["ParsedResults"][0]["ParsedText"]
