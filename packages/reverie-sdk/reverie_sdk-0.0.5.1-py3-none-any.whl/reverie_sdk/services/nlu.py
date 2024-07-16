import requests, json, typing
from reverie_sdk.base import BaseModel


class ReverieLangIdTextResponse:
    def __init__(self, **data) -> None:
        self.lang: str = data.get("lang", None)
        self.confidence: float = data.get("confidence", None)

    def __str__(self) -> str:
        return f"""ReverieLangIdTextResponse(
    lang        = {self.lang}
    confidence  = {self.confidence}
)""".strip()

    def __repr__(self) -> str:
        return str(self)


class ReverieNLU(BaseModel):
    def __init__(self, api_key: str, app_id: str, verbose: bool = False) -> None:
        super().__init__(api_key=api_key, app_id=app_id, verbose=verbose)
        self._logger.debug("NLU module initialized!")

    def train_model(
        self,
        src_lang: str,
        common_examples: typing.List[typing.Dict[str, str]],
        intent_keywords: typing.Dict,
    ):
        url = "https://revapi.reverieinc.com/train"

        headers = {
            "REV-API-KEY": self._api_key,
            "REV-APPNAME": "nlu",
            "REV-APP-ID": self._app_id,
            "Content-Type": "application/json",
            "src_lang": src_lang,
        }

        response = requests.request(
            "POST",
            url,
            headers=headers,
            data={
                "config": {"language": src_lang},
                "textspace_data": {
                    "intent_keywords": intent_keywords,
                    "common_examples": common_examples,
                },
            },
        )

        return response.json()

    def test_model(self, data):
        url = "https://revapi.reverieinc.com"

        headers = {
            "REV-API-KEY": self.api_key,
            "REV-APPNAME": "nlu",
            "REV-APP-ID": self.app_id,
            "Content-Type": "application/json",
        }

        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=data,
        )

        return response.json()

    def lang_id_text(
        self,
        text: str,
        max_length: typing.Union[int, None] = None,
    ):
        url = "https://revapi.reverieinc.com/"

        payload = json.dumps(
            {
                "text": text,
                **({"max_length": max_length} if max_length else {}),
            }
        )
        headers = {
            "REV-APP-ID": self._app_id,
            "REV-API-KEY": self._api_key,
            "REV-APPNAME": "lang_id_text",
            "Content-Type": "application/json",
        }

        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=payload,
        )

        return ReverieLangIdTextResponse(**response.json())
