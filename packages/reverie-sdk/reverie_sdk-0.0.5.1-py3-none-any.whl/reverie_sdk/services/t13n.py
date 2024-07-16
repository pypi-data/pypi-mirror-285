import json, typing
from reverie_sdk.base import *
import requests


class ReverieT13nResponse:
    class Result:
        def __init__(
            self,
            apiStatus: int = None,
            inString: str = None,
            outString: typing.List[str] = None,
        ) -> None:
            self.apiStatus: int = apiStatus
            self.inString: str = inString
            self.outString: typing.List[str] = outString

        def __str__(self) -> str:
            outString = "\n".join([((" " * 8) + e.strip()) for e in self.outString])
            return f"""ReverieT13nResponse.Result(
    apiStatus   : {self.apiStatus}
    inString    : {self.inString}
    outString   : 
{outString}
)""".strip()

        def __repr__(self) -> str:
            return str(self)

    def __init__(
        self,
        status: str = None,
        message: str = None,
        error_cause: str = None,
        responseList: typing.List[dict] = None,
        **kwargs,
    ) -> None:
        self.responseList: typing.List[ReverieT13nResponse.Result] = (
            [ReverieT13nResponse.Result(**e) for e in responseList]
            if responseList
            else None
        )
        self.kwargs = kwargs
        self.status: str = status
        self.message: str = message
        self.error_cause: str = error_cause

    def __str__(self) -> str:
        if self.responseList:
            responseList: str = "\n".join(map(str, self.responseList or []))
            responseList = "\n" + "\n".join(
                [((" " * 8) + e) for e in responseList.splitlines()]
            )
        else:
            responseList = None

        return f"""
ReverieT13nResponse(
    status          : {self.status}
    message         : {self.message}
    error_cause     : {self.error_cause}
    responseList    : {responseList}
    kwargs          : {self.kwargs}
)
    """.strip()


class ReverieT13N(BaseModel):
    def __init__(self, api_key: str, app_id: str, verbose: bool = False) -> None:
        super().__init__(api_key=api_key, app_id=app_id, verbose=verbose)
        self._logger.debug("T13N module initialized!")

    def transliteration(
        self,
        data: typing.List[str],
        src_lang: str,
        tgt_lang: str,
        cnt_lang: str,
        domain: str = "1",
        isBulk: bool = True,
        abbreviate: bool = True,
        noOfSuggestions: int = 1,
        convertNumber: str = "local",
        ignoreTaggedEntities: bool = False,
        url="https://revapi.reverieinc.com/",
    ) -> ReverieT13nResponse:
        """
        T13N Transliterate

        :param src_lang: The script used in the input text
        :param tgt_lang: The script to which you want to convert the input text
        :param domain: The Domain refers to the universe in which you use the Transliteration API
        :param cnt_lang: The language of the words in the input text
            Example -
            “data”: “Singh Sahab aap Kahan the.”
            In the example above, the Hindi language words are written in the English language script (Roman Script). So cnt_lang = "hi"

        :param data: typing.List of input text for transliteration.
        :param isBulk: Specify whether the API should initially search in the Exception DB to transliterate the input text. Note - By default, the isBulk= true and will not search in the Exception DB.
        :param noOfSuggestions:  Number of transliteration suggestions the API should return for the input text. Note - By default, the noOfSuggestions = 1, means the API will return only one transliteration suggestion for the input string.
            Example -
            Consider noOfSuggestions = 2
            Source Content      Target Content
            Rama                1.      रामा
                                2.      रमा

        :param abbreviate: The abbreviate will Validate whether any Abbreviations/ Acronyms are passed in the input text and will transliterate it accurately.
            Note - By default, the abbreviate = true
            Note - if the value is false, then the API will consider the abbreviation as a word and will transliterate to the nearest available word.
            Note - In the input text, pass the abbreviations in the upper case.

        :param convertNumber: Specify whether to convert the numbers in the input text to the target language script.
            Note - By default, the convertNumber = false
            Example -
            Consider convertNumber = true
            Source string       Target string
            2020.04             २०२०.०४

        """

        payload = json.dumps(
            {
                "data": data,
                "isBulk": isBulk,
                "abbreviate": abbreviate,
                "convertNumber": convertNumber,
                "noOfSuggestions": noOfSuggestions,
                "ignoreTaggedEntities": ignoreTaggedEntities,
            }
        )
        headers = {
            "Content-Type": "application/json",
            "REV-API-KEY": self._api_key,
            "REV-APP-ID": self._app_id,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "domain": str(domain),
            "cnt_lang": cnt_lang,
            "REV-APPNAME": "transliteration",
        }

        try:
            response = requests.request(
                "POST",
                url,
                headers=headers,
                data=payload,
            )
            return ReverieT13nResponse(**response.json())
        except Exception as err:
            self._logger.error(
                json.dumps(
                    {
                        "response.status_code": response.status_code,
                        "response.text": response.text,
                    }
                )
            )
