import sys
import time
import traceback
from typing import Callable, Dict

from dalpha.data_update_consumer import DataUpdateItem
from dalpha.dto import UpdateResult
from dalpha.logging import logger
from dalpha.exception import ExpectedError, WaitException
from dalpha.update_agent import UpdateAgent

class DalphaDataUpdater:
    def __init__(
        self,
        process: Callable[[Dict, DataUpdateItem, bool], UpdateResult],
        load_globals: Callable[[], Dict],
        kafka_topic: str = "",
        api_id: int = 0,
        alert: bool = False
    ):
        self.wait_flag = True

        self.update_agent = UpdateAgent(kafka_topic, api_id=api_id)
        self.process = process
        self.globals = load_globals()
        self.api_id = api_id
        self.alert = alert

    def _poll_input(self):
        try:
            input_json =  self.update_agent.poll()
        except SystemExit:
            logger.info("SystemExit caught, exiting.")
            sys.exit(0)
        except Exception as e:
            logger.warning(f"Error during update_poll: {e}")
            input_json = None
        
        if input_json is None:
            if self.wait_flag:
                logger.info("waiting...")
                self.wait_flag = False
            raise WaitException("No input_json")
        else:
            return input_json


    def _pipeline(self):
        try:
            input_json = self._poll_input()
        except WaitException:
            return
        
        logger.info("processing...")

        try:
            logger.info("Data update starts...")
            update_start_time = time.time()
            data_update_result: UpdateResult = self.process(
                globals = self.globals,
                data_update_item = input_json,
                use_mock = False
            )
            update_end_time = time.time()
            logger.info(f"Data update is done. Time taken: {update_end_time - update_start_time:.2f} sec")
        except ExpectedError as expected_error:
            self.update_agent.validate_error(output=expected_error.error_json, alert=self.alert)
            self.update_agent.close()

            return
        except Exception as unexpected_error:
            error_message = f"Unexpected error occurred while data update : \033[31m{unexpected_error}\033[0m\n{traceback.format_exc()}\n"
            logger.error(error_message)
            error_json = {"reason": f"Unexpected error occurred while data update: {unexpected_error}"}
            self.update_agent.validate_error(output=error_json, alert=self.alert)
            self.update_agent.close()

            return
        finally:
            self.wait_flag = True
        
        self.update_agent.validate(
            output = data_update_result.output_json,
            alert = self.alert
        )
        self.update_agent.close()

    def run(self):
        self._pipeline()
