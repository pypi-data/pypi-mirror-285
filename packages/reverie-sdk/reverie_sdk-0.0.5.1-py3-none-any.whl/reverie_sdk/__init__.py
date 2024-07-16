from reverie_sdk.base import *
from reverie_sdk.services import *


class ReverieClient(BaseModel):
    """
    Wrapper class for all underlying Reverie services:
    - ASR/ STT
    - TTS
    - T13N
    - NMT
    - NLU
    - NLP
    """

    def __init__(
        self,
        api_key: str,
        app_id: str,
        verbose: bool = False,
    ) -> None:
        """
        Reverie Python3 SDK Client

        Wrapper class for all underlying Reverie services:
        - ASR/ STT
        - TTS
        - T13N
        - NMT
        - NLU
        - NLP

        :param api_key: A unique key/token is provided by Reverie to identify the user using the STT API.
        :param app_id: A unique account ID to identify the user and the default account settings.
        :param verbose: Noisy logging, extra details
        """

        super().__init__(api_key=api_key, app_id=app_id, verbose=verbose)

        creds = dict(api_key=api_key, app_id=app_id, verbose=verbose)
        self.asr: ReverieASR = ReverieASR(**creds)
        """
            ASR/ STT related services:
                - STT Streaming
                - STT File (non streaming)
                - STT Batch
        """

        self.tts: ReverieTTS = ReverieTTS(**creds)
        """
            TTS related services
        """

        self.t13n = ReverieT13N(**creds)
        """
            Transliteration related services
        """

        self.nmt = ReverieNMT(**creds)
        """
            Translation related services
        """

        self.nlu = ReverieNLU(**creds)
        """
            Sansadhak services
        """

        self._logger.debug("All modules initialized!")

    def __mask_cred(self, val: str):
        masked_val = "x" * 8 + val[-4:]
        print(len(val), len(masked_val))
        return masked_val

    def __str__(self) -> str:
        return f"""{self.__class__.__name__} (
    api_key = {self.__mask_cred(self._api_key)}
    app_id  = {self.__mask_cred(self._app_id)}
    verbose = {self._verbose}
    modules:
        - asr   = {self.asr}
        - t13n  = {self.t13n}
        - tts   = {self.tts}
)""".strip()

    def __repr__(self) -> str:
        return str(self)
