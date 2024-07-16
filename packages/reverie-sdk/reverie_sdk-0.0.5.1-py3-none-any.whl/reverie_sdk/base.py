import logging


class BaseModel:
    def __init__(
        self,
        api_key: str,
        app_id: str,
        verbose: bool = False,
    ) -> None:
        self._api_key = api_key
        self._app_id = app_id
        self._verbose: bool = verbose

        logging.basicConfig(
            format=(
                "[%(asctime)s] "
                "%(filename)s, %(lineno)d "
                "| %(levelname)5s "
                "| %(processName)s "
                "| %(threadName)s "
                "| %(message)s"
            ),
        )
        logger = logging.getLogger("Reverie SDK")

        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)

        self._logger: logging.Logger = logger
