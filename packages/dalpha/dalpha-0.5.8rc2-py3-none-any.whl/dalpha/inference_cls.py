import json
import sys
import time
import traceback
from copy import deepcopy
from typing import Callable, Dict, List, Literal, Optional, Tuple, Union

from dalpha.agent import Agent
from dalpha.dto import InferenceResult
from dalpha.exception import ExpectedError, WaitException
from dalpha.logging import logger
from dalpha.message_consumer import EvaluateItem
import inspect


class DalphaAI:
    def __init__(
        self,
        api_id: int,
        inference: Callable[[Dict, EvaluateItem, bool], InferenceResult],
        load_globals: Callable[[], Dict],
        mock_file: Optional[str],
        mocks_file: Optional[str],
    ):
        self.wait_flag = True

        self.agent = Agent(api_id=api_id)
        self.inference = inference
        self.globals = load_globals()

        self.is_mock, self.mock_info, self.mocks = self._init_mock(mock_file=mock_file, mocks_file=mocks_file)

    def _init_mock(
        self, mock_file: bool, mocks_file: bool
    ) -> Tuple[bool, Union[str, Literal["NO MOCK"]], List[Dict[str, any]]]:
        MOCK_STRUCTURE = "mock/mock_structure.json"
        MOCK_DATA = f"mock/{mock_file}"
        MOCKS_DATA = f"mock/{mocks_file}"
        MOCKS_START_EVAL_ID = 10001

        is_mock = False
        mock_info = "NO MOCK"
        mocks = []

        # load structure
        try:
            with open(MOCK_STRUCTURE, "r") as file:
                mock_structure = json.load(file)
        except FileNotFoundError:
            logger.error(f"mock_structure.json not found!")
            sys.exit(1)

        # add metadata
        if mock_file:
            is_mock = True
            mock_info = MOCK_DATA
            try:
                with open(MOCK_DATA, "r") as file:
                    mock = deepcopy(mock_structure)
                    metadata = json.load(file)
                    mock["metadata"] = metadata
                    mocks.append(mock)
            except FileNotFoundError:
                logger.error(f"{MOCK_DATA} not found!")
                sys.exit(1)

        elif mocks_file:
            is_mock = True
            mock_info = MOCKS_DATA
            try:
                with open(MOCKS_DATA, "r") as file:
                    metadata_list = json.load(file)
                    for idx, metadata in enumerate(metadata_list):
                        mock = deepcopy(mock_structure)
                        mock["id"] = MOCKS_START_EVAL_ID + idx
                        mock["metadata"] = metadata
                        mocks.append(mock)
            except FileNotFoundError:
                logger.error(f"{MOCKS_DATA} not found!")
                sys.exit(1)

        return is_mock, mock_info, mocks

    def _poll_input(self):
        input_json = None
        try:
            input_json = self.agent.poll(mock=self.is_mock)
        except SystemExit:
            logger.info("sys.exit() worked as expected")
            sys.exit(0)
        except Exception as e:
            logger.warning(f"agent.poll not working! {e}")
            input_json = None

        if input_json is None:
            if self.wait_flag:
                logger.info("waiting...")
                self.wait_flag = False
            raise WaitException("No input_json")
        else:
            return input_json

    def _pipeline(self):
        # poll input_json
        try:
            input_json = self._poll_input()
        except WaitException:
            return

        logger.info(f"\n\033[31m\n\t| MOCK DATA : {self.mock_info}\n\033[0m")
        logger.info("processing...")

        try:
            # read input.
            # dynamic-type 으로 만든 경우 metadata가 input과 같습니다.
            eval_id, account_id, metadata = (
                input_json.id,
                input_json.accountId,
                input_json.metadata
            )
        except KeyError as e:
            logger.warning(f"input_json format is not correct!")
            error_json = {"reason": f"input_json format is not correct!\n{e}"}
            self.agent.validate_error(evaluate_id=eval_id, output=error_json, mock=self.is_mock)
            self.wait_flag = True
            return

        # inference
        try:
            logger.info("AI inference starts...")
            inference_start_time = time.time()

            if inspect.isgeneratorfunction(self.inference):
                last_usage = 1
                last_output = None
                for inference_result in self.inference(
                    globals=self.globals,
                    evaluate_item=input_json,
                    use_mock=self.is_mock
                ):
                    self.agent.stream_validate(
                        evaluate_id = eval_id,
                        output = inference_result.output_json,
                        usage = inference_result.usage,
                    )
                    last_usage = inference_result.usage
                    last_output = inference_result.output_json
                inference_result: InferenceResult = InferenceResult(
                    output_json = last_output,
                    usage = last_usage
                )
                
            else:
                inference_result: InferenceResult = self.inference(
                    globals=self.globals,
                    evaluate_item=input_json,
                    use_mock = self.is_mock
                )
            inference_end_time = time.time()
            logger.info(f"AI inference is done. Time taken: {inference_end_time - inference_start_time:.2f} sec")
            self.agent.validate(
                evaluate_id=eval_id,
                output=inference_result.output_json,
                mock=self.is_mock,
                usage=inference_result.usage,
            )
        except ExpectedError as expected_error:
            self.agent.validate_error(evaluate_id=eval_id, output=expected_error.error_json, mock=self.is_mock, error_code=expected_error.error_code)
            self.wait_flag = True
            return
        except Exception as unexpected_error:
            error_message = f"Unexpected error occurred while running ai : \033[31m{unexpected_error}\033[0m\n{traceback.format_exc()}\n"
            logger.error(error_message)
            error_json = {"reason": f"Unexpected error occurred while running ai: {unexpected_error}"}
            self.agent.validate_error(evaluate_id=eval_id, output=error_json, mock=self.is_mock)
            self.wait_flag = True
            return
        finally:
            self.wait_flag = True

    def run_pipeline(self):
        if self.is_mock:
            for mock in self.mocks:
                self.agent.set_mock(mock)
                self._pipeline()
        else:
            self._pipeline()

    def run(self):
        if self.is_mock:
            logger.info("MOCK.. just running once")
            self.run_pipeline()
        else:
            while True:
                self.run_pipeline()
