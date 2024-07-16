import json, os, warnings, queue, stream2sentence as s2s
import typing, re, requests, threading, io, pydub, wave
from pathlib import Path
from reverie_sdk.utils import threadsafe_generators as tsg, formatters as fmt, chunker
from reverie_sdk.base import BaseModel


class ReverieTtsResponse:
    def __init__(
        self,
        audio_bytes: bytes = None,
        **kwargs,
    ) -> None:
        self.audio_bytes: bytes = audio_bytes
        self.message: str = str(kwargs.get("message", "")).strip()
        self.status: str = str(kwargs.get("status", "")).strip()
        self.kwargs: typing.Dict = kwargs
        self.duration: float = None
        self.format: str = kwargs.get("format", None)
        self.channels: int = kwargs.get("channels", None)
        self.sample_rate: int = kwargs.get("sample_rate", None)

        if self.audio_bytes:
            try:
                io_file = io.BytesIO(self.audio_bytes)
                if (self.format or "").lower() == "pcm":
                    io_file = io.BytesIO()
                    with wave.open(io_file, "wb") as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(self.sample_rate or 16000)
                        wav_file.writeframes(self.audio_bytes)

                audio: pydub.AudioSegment = pydub.AudioSegment.from_file(
                    io_file,
                    format={"pcm": "wav"}.get(self.format.lower(), self.format),
                    # codec={"opus": "libopus"}.get(self.format.lower(), None),
                )
                self.duration = audio.duration_seconds
                self.channels = audio.channels
            except Exception as err:
                pass
                # print(err)

    def save_audio(
        self,
        file_path: typing.Union[str, Path, os.PathLike],
        create_parents=False,
        overwrite_existing=False,
    ):
        if self.audio_bytes is None:
            raise Exception(f""" Nothing to save! """.strip())

        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        if os.path.exists(file_path) and not overwrite_existing:
            raise Exception(f""" file_path="{file_path}" already exists! """.strip())

        if not os.path.exists(file_path.parent):
            if not create_parents:
                raise Exception(
                    f""" file_path.parent="{file_path.parent}" doesn't exist! """.strip()
                )
            else:
                os.makedirs(file_path.parent, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(self.audio_bytes)

    def __str__(self) -> str:
        return f"""ReverieTtsResponse(
    status          : {self.status}
    message         : {json.dumps(self.message) if self.message else self.message}
    format          : {self.format}
    sample_rate     : {self.sample_rate}
    audio_bytes     : {len(self.audio_bytes) if self.audio_bytes else None}
    duration        : {fmt.duration_formatted(self.duration) if self.duration is not None else self.duration}
    kwargs          : {self.kwargs}
)""".strip()


class ReverieTTS(BaseModel):
    "Text to speech"

    def __init__(self, api_key: str, app_id: str, verbose: bool = False) -> None:
        super().__init__(api_key=api_key, app_id=app_id, verbose=verbose)
        self._logger.debug("TTS module initialized!")

    def tts(
        self,
        text: typing.Union[str, typing.List[str]] = None,
        ssml: typing.Union[str, typing.List[str]] = None,
        speaker: str = None,
        speed: float = 1.0,
        pitch: float = 0,
        sample_rate: int = 22050,
        format: str = "WAV",
        url: str = "https://revapi.reverieinc.com/",
    ) -> ReverieTtsResponse:
        """
        You can use the Text-to-Speech (TTS) API to convert any text to speech.

        :param text
        :param ssml
            The plain text or SSML input to synthesize an audio output. If you want to follow W3 standards, the ssml field must be used and not the text field.
        :param speaker: Describes which speaker to use for synthesis
        :param speed: The speech rate of the audio file. Allows values: from 0.5 (slowest speed rate) up to 1.5 (fastest speed rate).
            Default: 1.0
        :param pitch: Speaking pitch, in the range. Allows values: from -3 up to 3. 3 indicates an increase of 3 semitones from the original pitch. -3 indicates a decrease of 3 semitones from the original pitch.
            Default: 0 (zero)
        :param sample_rate: The sampling rate (in hertz) to synthesize the audio output
            Default: 22050
        :param format: The speech audio format to generate the audio file
            Default: "WAV"

        :returns ReverieTtsResponse
        """

        if not isinstance(speaker, str):
            raise Exception(f"`speaker` should be string, found {type(speaker)}!")

        if text is None and ssml is None:
            raise Exception(f"""Either `text` or `ssml` must be provided!""".strip())

        if text is not None and ssml is not None:
            warnings.warn(
                UserWarning(
                    f"""Both `text` and `ssml` are provided, using `ssml` for synthesis!""".strip()
                )
            )

        payload = json.dumps(
            {
                **({"ssml": ssml} if ssml else {"text": text}),
                "speed": speed,
                "pitch": pitch,
                "sample_rate": sample_rate,
                "format": format,
            },
            # ensure_ascii=False, # TODO
        )
        self._logger.debug(f"payload: {payload}")

        headers = {
            "REV-API-KEY": self._api_key,
            "REV-APP-ID": self._app_id,
            "REV-APPNAME": "tts",
            "speaker": speaker,
            "Content-Type": "application/json",
        }
        self._logger.debug(f"headers: {headers}")

        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=payload,
        )

        if response.status_code == 200:
            return ReverieTtsResponse(
                audio_bytes=response.content,
                src=dict(text=text, ssml=ssml),
                sample_rate=sample_rate,
                format=format,
            )

        try:
            return ReverieTtsResponse(
                **response.json(),
                headers=headers,
                src=dict(text=text, ssml=ssml),
            )
        except Exception as e:
            print(e)
            return ReverieTtsResponse(
                message=response.text,
                status=response.status_code,
                headers=headers,
                src=dict(text=text, ssml=ssml),
            )

    def _tts_streaming_worker(self, kwargs: typing.Dict, *a, **kw):
        return self.tts(**kwargs)

    def tts_streaming(
        self,
        # reverie API related
        text: str,
        speaker: str = None,
        speed: float = 1.0,
        pitch: float = 0,
        sample_rate: int = 22050,
        format: str = "WAV",
        url: str = "https://revapi.reverieinc.com/",
        # tokenize
        fast_sentence_fragment: bool = True,
        tokenizer: str = "nltk",
        tokenizer_language: str = "en",
        sentence_fragment_delimiters: str = ".?!;:,\n…)]}。-",
        max_words_per_chunk=15,
    ) -> typing.Generator[ReverieTtsResponse, None, None]:

        done = False
        resp_queue = queue.Queue()

        sentence_queue = queue.Queue()

        # split text
        char_iterator = tsg.CharIterator()
        char_iterator.add(text)
        acc_generator = tsg.AccumulatingThreadSafeGenerator(char_iterator)

        s2s.init_tokenizer(tokenizer)
        sentences = s2s.generate_sentences(
            tokenizer=tokenizer,
            generator=acc_generator,
            cleanup_text_links=True,
            cleanup_text_emojis=True,
            language=tokenizer_language,
            sentence_fragment_delimiters=sentence_fragment_delimiters,
            quick_yield_single_sentence_fragment=fast_sentence_fragment,
            force_first_fragment_after_words=max_words_per_chunk,
        )

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 0:
                for chunk in chunker.chunk_sentence(sentence, max_words_per_chunk):
                    chunk = chunk.strip()
                    if len(chunk) > 0:
                        sentence_queue.put(chunk)
            else:
                continue  # Skip empty sentences

        sentence_queue.put(None)

        def process_text():
            # process sentence
            while True:
                try:
                    sentence = sentence_queue.get()
                    if sentence is None:  # Sentinel value to stop the worker
                        break

                    resp = self.tts(
                        text=sentence,
                        format=format,
                        pitch=pitch,
                        sample_rate=sample_rate,
                        speaker=speaker,
                        speed=speed,
                        url=url,
                    )

                    resp_queue.put(resp)
                except Exception as err:
                    self._logger.error(err)
                    break

            nonlocal done
            done = True

        worker = threading.Thread(target=process_text)
        worker.start()

        while not done:
            if not resp_queue.empty():
                yield resp_queue.get()

        worker.join()
