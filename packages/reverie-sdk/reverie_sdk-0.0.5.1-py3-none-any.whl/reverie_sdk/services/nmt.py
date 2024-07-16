import json, typing
import requests
from reverie_sdk.base import *


class ReverieLocalizationResult:
    class ReverieLocalizationResponseItem:
        def __init__(self, **data) -> None:
            self.inString: str = data.get("inString", None)
            self.apiStatus: int = data.get("apiStatus", None)
            self.outString: str = data.get("outString", None)
            self.outStrings: typing.Dict[str, str] = data.get("outStrings", None)
            self.api_statuses: typing.Dict[str, int] = data.get("api_statuses", None)
            self.message: str = data.get("message", None)
            self.status: str = data.get("status", None)

        def __str__(self) -> str:
            outStrs = ""
            apiStatuses = ""

            if self.outStrings:
                for k, v in self.outStrings.items():
                    outStrs += f"{' '*8}{k} : {v}\n"

                for k, v in self.api_statuses.items():
                    apiStatuses += f"{' '*8}{k} : {v}\n"

            return (
                f"""{self.__class__.__name__}(\n"""
                f"""    status      = {self.status}\n"""
                f"""    message     = {self.message}\n"""
                f"""    inString    = {self.inString}\n"""
                f"""    apiStatus   = {self.apiStatus}\n"""
                f"""    outString   = {self.outString}\n"""
                f"""    outStrings:\n{outStrs}\n"""
                f"""    api_statuses:\n{apiStatuses}\n"""
                """)"""
            )

        def __repr__(self) -> str:
            return str(self)

    def __init__(
        self,
        **resp,
    ) -> None:
        self._raw_response = resp
        # print(resp)
        self.responseList: typing.List[self.ReverieLocalizationResponseItem] = [
            self.ReverieLocalizationResponseItem(**e)
            for e in resp.get("responseList", [])
        ]
        self.tokenConsumed: int = resp.get("tokenConsumed", None)

    def __str__(self) -> str:
        responseList = "\n".join(str(e) for e in self.responseList).splitlines(True)
        responseList = "".join((" " * 8 + l) for l in responseList)

        return (
            f"""{self.__class__.__name__}(\n"""
            f"""    responseList:\n{responseList}\n"""
            f"""    tokenConsumed: {self.tokenConsumed}\n"""
            f""")"""
        )

    def __repr__(self) -> str:
        return str(self)


class ReverieNMT(BaseModel):
    def __init__(self, api_key: str, app_id: str, verbose: bool = False) -> None:
        super().__init__(api_key=api_key, app_id=app_id, verbose=verbose)
        self._logger.debug("NMT module initialized!")

    def localization(
        self,
        data: typing.List,
        src_lang: str,
        tgt_lang: typing.Union[str, typing.List[str]],
        domain: str,
        nmtParam: bool = False,
        dbLookupParam: bool = False,
        segmentationParam: bool = False,
        builtInPreProc: bool = False,
        debugMode: bool = False,
        usePrabandhak: bool = False,
        nmtMask: bool = True,
        nmtMaskTerms: typing.List[str] = None,
        url: str = "https://revapi.reverieinc.com/",
    ) -> ReverieLocalizationResult:
        """
        NMT Localization

        Parameters
        ----------
        src_lang: string
            The language of the input text
            Mention the ISO Language code of the input text.

        tgt_lang: string or list of strings
            Language to which you want to localize the input text
            Note- To enter multiple target languages, separate the value using the comma separator(,).
            For example: “tgt_lang” : “hi, ta”
            Mention the ISO Language code of the target language.

        domain: string
            The Domain refers to the universe in which you use the Transliteration API.
            Example- Health Care, Insurance, Legal, etc.
            Mention the domain ID.
            Note- The default domain = 1

        data: array of content
            List of input text for localization.

        dbLookupParam: boolean
            The parameter will specify whether the application should refer to the Lookup DB or not.
            i.e., when the dbLookupParam is True, the system will initially refer to the Database to fetch contents.
            Note - By default, the dbLookupParam= false.

        segmentationParam: boolean
            The parameter will specify whether the content should be segmented before localizing the input.
            Note - By default, the segmentationParam= false.

        nmtParam: boolean
            Specify whether the content localization process should use NMT technology or not.
            i.e., When the nmtParam value is True, the system will initially refer to the Lookup database to localize content. If the content is not available in the database, then the NMT is used for translation.
            Note - By default, the nmtParam= false

        builtInPreProc: boolean
            Specify whether you want to pre-process the input and tag the strings according to patterns in the regex_pattern table
            Note - By default, the builtInPreProc= false

        debugMode: boolean
            The Debug parameter will provide log details about localized content.
            The details provided are the entity code, localization process type, and more. This information is useful to capture the log and analyze the system performance.
            Note - By default, the debugMode= false

        usePrabandhak: boolean
            Specify whether you want to verify the unmoderated strings.
            Set usePrabandhak = true, then the API will send the unverified strings to the Prabandhak application for verification.
            Note - By default, the usePrabandhak= false.
            Note - The usePrabandhak parameter is enabled only for the Reverie's Manual Verification Service subscribers.

        Returns
        -------
        inString: string
            The input text in the source language.

        outString: string
            The localized content in the requested target language(s).

        api_status: integer
            Status of API - Moderated / Partial /Unmoderated (Aggregate of all segments).
            Refer to section Appendix B: API Messages to know about the available api_status and its description.

        status: string
            Error status code for the invalid request.
            Note - The status is shown only for the invalid request.

        error_cause: string
            A Human-readable error message.
            Refer to section Appendix B: API Messages to know more about the error messages and description.

        tokenConsumed: integer
            The payload length served by NMT.
            Note - if LookUp DB serves the payload and if the content is moderated, then the tokenConsumed = zero (0).
        """

        payload = json.dumps(
            {
                "data": data,
                "nmtParam": nmtParam,
                "dbLookupParam": dbLookupParam,
                "segmentationParam": segmentationParam,
                "builtInPreProc": builtInPreProc,
                "debugMode": debugMode,
                "usePrabandhak": usePrabandhak,
                "nmtMask": nmtMask,
                "nmtMaskTerms": nmtMaskTerms,
            }
        )
        headers = {
            "Content-Type": "application/json",
            "REV-API-KEY": self._api_key,
            "REV-APP-ID": self._app_id,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang if isinstance(tgt_lang, str) else ",".join(tgt_lang),
            "domain": str(domain),
            "REV-APPNAME": "localization",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return ReverieLocalizationResult(**response.json())
