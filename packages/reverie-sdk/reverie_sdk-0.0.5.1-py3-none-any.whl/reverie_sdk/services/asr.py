import io, queue
import json
import threading
import time
import traceback
import typing
import requests
from websocket import WebSocket, create_connection, WebSocketBadStatusException
from reverie_sdk.base import BaseModel


class ReverieAsrResult:
    def __init__(
        self,
        id: str = None,
        text: str = None,
        final: bool = None,
        cause: str = None,
        success: bool = None,
        confidence: str = None,
        display_text: str = None,
    ) -> None:
        self.id: str = id
        self.text: str = text
        self.final: bool = final
        self.cause: str = cause
        self.success: bool = success
        self.confidence: str = confidence
        self.display_text: str = display_text

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return (
            f"""{self.__class__.__name__} (\n"""
            f"""    id           : {self.id}\n"""
            f"""    text         : {self.text}\n"""
            f"""    final        : {self.final}\n"""
            f"""    cause        : {self.cause}\n"""
            f"""    success      : {self.success}\n"""
            f"""    confidence   : {self.confidence}\n"""
            f"""    display_text : {self.display_text}\n"""
            f""")"""
        ).strip()


class ReverieAsrBatchResult:
    class ReverieAsrBatchTranscript:
        class ReverieAsrBatchWord:
            def __init__(
                self,
                data: typing.Dict,
                dur_width: int = 8,
                word_width: int = 8,
                sent_width: int = 8,
            ) -> None:
                self.sent_idx: int = data.get("sent_idx", None)
                self.conf: float = data.get("conf", None)
                self.end: float = data.get("end", None)
                self.start: float = data.get("start", None)
                self.word: str = data.get("word", None)

                self._dur_width: int = dur_width
                self._word_width: int = word_width
                self._sent_width: int = sent_width
                # including decimal part ".xx" (5 + . + 2)

            def __repr__(self) -> str:
                return str(self)

            def __str__(self) -> str:
                return (
                    f"""{self.__class__.__name__}( """
                    f"""sent  : {str(self.sent_idx).rjust(self._sent_width)}, """
                    f"""start : {f"%{self._dur_width + 3}.2f" % (self.start)}, """
                    f"""end   : {f"%{self._dur_width + 3}.2f" %(self.end)}, """
                    f"""conf  : {self.conf:.3f}, """
                    f"""word  : {self.word.ljust(self._word_width)} )"""
                ).strip()

        def __init__(self, data: typing.Dict) -> None:
            try:
                self.transcript: str = data.get("transcript", None)
                self.channel_number: str = data.get("channel_number", None)
                self.words: str = data.get("words", None)

                if isinstance(self.words, list) and len(self.words) > 0:
                    words = []
                    sent_width = len(str(len(self.words)))

                    for sent_idx, sent in enumerate(self.words, 1):
                        if isinstance(sent, list):
                            words.extend({**w, "sent_idx": sent_idx} for w in sent)
                        else:
                            words.append({**sent, "sent_idx": sent_idx})

                    self.words = words
                    dur_width = len(str(int(self.words[-1]["end"])))
                    word_width = len(
                        sorted(self.words, key=lambda x: len(x["word"]), reverse=True,)[
                            0
                        ]["word"]
                    )

                    for word_idx, w in enumerate(self.words):
                        self.words[word_idx] = self.ReverieAsrBatchWord(
                            w,
                            dur_width=dur_width,
                            word_width=word_width,
                            sent_width=sent_width,
                        )

            except Exception as e:
                print(e)
                print(data)

        def __repr__(self) -> str:
            return str(self)

        def __str__(self) -> str:
            words = self.words or []
            if len(words) <= 5:
                words_display = "\n".join(map(str, words)).splitlines(True)
            else:
                words_display = ("\n".join(map(str, words[:2])) + "\n").splitlines(True)
                words_display += [f"... ({len(self.words)-4} more words) ...\n"]
                words_display += "\n".join(map(str, words[-2:])).splitlines(True)

            words_display = "".join([(" " * 8) + e for e in words_display])
            return (
                f"""{self.__class__.__name__} (\n"""
                f"""    transcript      : {self.transcript}\n"""
                f"""    channel_number  : {self.channel_number}\n"""
                f"""    words           : ({len(self.words)})\n"""
                f"""{words_display}\n"""
                f""")"""
            ).strip()

    def __init__(self, data: typing.Dict) -> None:
        self._raw_response: typing.Dict = data

        self.code: str = data.get("code", None)
        self.job_id: str = data.get("job_id", None)
        self.status: str = data.get("status", None)
        self.result: str = data.get("result", None)
        self.message: str = data.get("message", None)

        if self.result:
            self.result = [self.ReverieAsrBatchTranscript(e) for e in self.result]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        result = "\n".join(map(str, self.result or [])).splitlines(True)
        result = "".join([(" " * 4) + e for e in result])
        return (
            f"""{self.__class__.__name__} (\n"""
            f"""    code    : {self.code}\n"""
            f"""    job_id  : {self.job_id}\n"""
            f"""    status  : {self.status}\n"""
            f"""    message : {self.message}\n"""
            f"""    result  :\n"""
            f"""    {result}\n"""
            f""")"""
        ).strip()


class AudioStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self):
        self.buff = queue.Queue()
        self.streaming: bool = True

    def add_chunk(self, in_data: bytes):
        """Continuously collect data from the audio stream, into the buffer."""
        if self.streaming:
            assert isinstance(in_data, bytes)
            self.buff.put(in_data)
        return self

    def generator(self):
        while self.streaming:
            data = b""
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk: bytes = self.buff.get()

            if chunk is None:
                yield data

            data += chunk

            # Now consume whatever other data's still buffered.
            while len(data) < 1024:
                try:
                    chunk = self.buff.get(block=False)
                    if chunk is None:
                        continue

                    data += chunk
                except queue.Empty:
                    break

            yield data


class ReverieASR(BaseModel):
    """Automatic Speech Recognition (ASR)/ Speech to Text (STT)"""

    def __init__(self, api_key: str, app_id: str, verbose: bool = False) -> None:
        super().__init__(api_key=api_key, app_id=app_id, verbose=verbose)
        self._logger.debug("ASR module initialized!")

    def __send_stream_data(
        self,
        ws: WebSocket,
        bytes_or_stream: typing.Union[AudioStream, bytes],
    ):
        if isinstance(bytes_or_stream, bytes):
            buffer = io.BytesIO(bytes_or_stream)
            try:
                while ws.connected:
                    d = buffer.read(4096)

                    if len(d) == 0:
                        break

                    ws.send_binary(d)
                    self._logger.debug(f"Sent {len(d)} bytes to ASR")
                    # time.sleep(0.01)

                if ws.connected:
                    ws.send_binary(b"--EOF--")
                    self._logger.debug(f"Sent EOF to ASR")
            except:
                self._logger.error(traceback.format_exc())

        elif isinstance(bytes_or_stream, AudioStream):
            try:
                for chunk in bytes_or_stream.generator():
                    if len(chunk) == 0 or not ws.connected:
                        break

                    ws.send_binary(chunk)
                    self._logger.debug(f"Sent {len(chunk)} bytes to ASR")
                    # time.sleep(0.01)

                if ws.connected:
                    ws.send_binary(b"--EOF--")
                    self._logger.debug(f"Sent EOF to ASR")
            except:
                bytes_or_stream.streaming = False
                self._logger.error(traceback.format_exc())

    def stt_stream(
        self,
        src_lang: str,
        bytes_or_stream: typing.Union[AudioStream, bytes],
        domain: str = "generic",
        timeout: float = 15,
        silence: float = 15,
        format: str = "16k_int16",
        host: str = "revapi.reverieinc.com",
        secure: bool = True,
        logging: str = "true",
        **extra_params,
    ) -> typing.Generator[ReverieAsrResult, None, None]:
        """
        Speech-to-Text Streaming v4.5.1

        :param src_lang: Language in which the audio is to be transcribed
        :param data: audio bytes
        :param domain: The universe in which the Streaming STT API is used for transcribing the speech
            default: "generic"
        :param timeout: The duration to keep a connection open between the application and the STT server; range = [1, 180]
            default: 15
        :param silence: The time to determine when to end the connection automatically after detecting the silence after receiving the speech data; range: [1, 30]
            default: 15
        :param format: The audio sampling rate and the data format of the speech
            default: 16k_int16
        :param host: default: "revapi.reverieinc.com"
        :param secure: Whether to use wss:// or ws://
            default: True
        :param logging: Describes how to treat client's logs

        :yields ReverieAsrStreamResult objects
        """

        self._logger.debug(f"extra_params: {extra_params}")

        url = f"{'wss' if secure else 'ws'}://{host}/stream?" + "&".join(
            f"{k}={v}"
            for k, v in {
                "appname": "stt_stream",
                "apikey": self._api_key,
                "appid": self._app_id,
                "domain": domain,
                "src_lang": src_lang,
                "timeout": timeout,
                "silence": silence,
                "format": format,
                "logging": logging,
                **extra_params,
            }.items()
        )

        try:
            ws = create_connection(url, enable_multithread=True)
        except WebSocketBadStatusException as e:
            err_msg = e.resp_body

            if isinstance(err_msg, bytes):
                err_msg = err_msg.decode()

            if isinstance(err_msg, str):
                try:
                    err_msg = json.loads(err_msg)
                except:
                    pass

            self._logger.error(err_msg)
            # self.logger.error(traceback.format_exc())
            yield ReverieAsrResult(success=False, text=err_msg["message"])
            return

        self._logger.debug(f"Websocket connected for url: {url}")

        t = threading.Thread(
            target=self.__send_stream_data,
            args=(ws, bytes_or_stream),
        )
        t.start()
        self._logger.debug("Started a thread to send audio chunks")

        while ws.connected:
            try:
                result = ws.recv()
                self._logger.debug(f"Raw ASR response: {result}")
                result = ReverieAsrResult(**json.loads(result))

                is_final = (result.final == True) or result.cause in [
                    "timeout",
                    "silence detected",
                    "EOF received",
                ]

                if is_final:
                    if isinstance(bytes_or_stream, AudioStream):
                        bytes_or_stream.streaming = False

                    ws.close()

                    yield result

                yield result
            except:
                self._logger.error(traceback.format_exc())
                break

    def stt_file(
        self,
        src_lang: str,
        data: bytes,
        domain: str = "generic",
        format: str = "16k_int16",
        url: str = "https://revapi.reverieinc.com/",
        logging: str = "true",
    ) -> ReverieAsrResult:
        """
        STT File (Non-Streaming) v4.2.2

        :param src_lang: Language in which the audio is to be transcribed
        :param data: audio bytes
        :param domain: The universe in which the Streaming STT API is used for transcribing the speech
            default: generic
        :param format: The audio sampling rate and the data format of the speech
            default: 16k_int16
        :param logging: Describes how to treat client's logs

        :return ReverieAsrStreamResult object
        """

        files = {"audio_file": data}

        headers = {
            "REV-APPNAME": "stt_file",
            "REV-API-KEY": self._api_key,
            "REV-APP-ID": self._app_id,
            "src_lang": src_lang,
            "domain": domain,
            "format": format,
            "logging": logging,
        }

        response = requests.request(
            "POST",
            url,
            headers=headers,
            files=files,
        )

        json_resp: typing.Dict = None
        try:
            json_resp: typing.Dict = response.json()
        except:
            pass

        if response.status_code != 200 or not isinstance(json_resp, dict):
            json_resp = json_resp or {}
            message = json_resp.get("message", response.text)
            self._logger.error(message)
            return ReverieAsrResult(success=False, text=message)

        return ReverieAsrResult(**json_resp)

    def stt_batch(
        self,
        src_lang: str,
        data: bytes,
        domain: str = "generic",
        format: str = "wav",
        base_url: str = "https://revapi.reverieinc.com/",
    ) -> typing.Generator[ReverieAsrBatchResult, None, str]:
        """
        STT Batch v1.2.1

        :param src_lang: string
        :param data: audio data
        :param domain: The universe in which the Streaming STT API is used for transcribing the speech
            default: "generic"
        :param format: The audio sampling rate and the data format of the speech
            default: "wav"
        """

        # initiate request
        url = f"{base_url.rstrip('/')}/upload"
        files = {"file": data}
        headers = {
            "src_lang": src_lang,
            "domain": domain,
            "format": format,
            "REV-API-KEY": self._api_key,
            "REV-APPNAME": "stt_batch",
            "REV-APP-ID": self._app_id,
        }

        response = requests.post(url, headers=headers, files=files)

        try:
            resp_data = ReverieAsrBatchResult(response.json())
            job_id = resp_data.job_id

            yield resp_data

            # check status
            url = f"{base_url.rstrip('/')}/status"
            headers = {
                "REV-API-KEY": self._api_key,
                "REV-APP-ID": self._app_id,
                "REV-APPNAME": "stt_batch",
            }
            params = (("job_id", job_id),)

            retries = 1
            success = False
            while not success:
                resp = requests.get(url, headers=headers, params=params)
                status_resp = ReverieAsrBatchResult(resp.json())

                yield status_resp

                if status_resp.code == "000":
                    success = True
                else:
                    wait = retries * 5
                    self._logger.debug(f"Sleeping for {wait} secs...")
                    time.sleep(wait)
                    retries += 1

            # get transcript
            url = f"{base_url.rstrip('/')}/transcript"
            headers = {
                "REV-API-KEY": self._api_key,
                "REV-APP-ID": self._app_id,
                "REV-APPNAME": "stt_batch",
            }

            resp = requests.request(
                "GET",
                url + f"?job_id={job_id}",
                headers=headers,
            )

            return ReverieAsrBatchResult(resp.json())
        except Exception as e:
            print(e)
            traceback.print_exc()
            return response.text
