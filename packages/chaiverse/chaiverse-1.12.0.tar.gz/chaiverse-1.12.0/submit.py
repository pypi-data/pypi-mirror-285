import itertools
import sys
import time
from typing import List, Optional

from pydantic import BaseModel, Extra, Field, PrivateAttr, validator


from chaiverse import config, errors, formatters, utils
from chaiverse.config import LEADERBOARD_ENDPOINT
from chaiverse.cli_utils.login_cli import auto_authenticate
from chaiverse.http_client import SubmitterClient
from chaiverse.lib.func import serialize_function
from chaiverse.schemas import DateRange


if 'ipykernel' in sys.modules:
    from IPython.core.display import display


class GenerationParams(BaseModel, extra=Extra.allow, title=''):
    temperature: float = Field(
        default=1.0,
        title="Temperature",
        description="Controls the randomness in the model's output. A higher temperature increases randomness."
    )
    top_p: float = Field(
        default=1.0,
        title="top_p",
        description="the model considers only the most probable tokens with probability above this threshold."
    )
    min_p: float = Field(
        default=0.0,
        title="min_p",
        description="Controls the minimum threshold a token must reach, relative to the top sampled token, in order for it to be sampled by your model."
    )
    top_k: int = Field(
        default=40,
        title="top_k",
        description="Number of highest probability tokens considered at each step of generation.")
    presence_penalty: Optional[float] = Field(
        default=0,
        title="presence_penalty",
        description="Encourages the model to use new and unique words by penalizing words that have already appeared in the text."
    )
    frequency_penalty: Optional[float] = Field(
        default=0,
        title="frequency_penalty",
        description="Encourages the model to use new and unique words by penalizing tokens based on their frequency in the text so far."
    )
    stopping_words: Optional[List[str]] = Field(
        default=["\n"],
        title="Stopping Words",
        description="Words or tokens that signal the model to stop generating further text.",
        # Determine how this field renders in HTML
        format="select2",
        unique_items=True,
        options={
            "select2": {
                "tokenSeparators": [" "],
            }
        }
    )
    max_input_tokens: Optional[int] = Field(
        default=config.DEFAULT_MAX_INPUT_TOKENS,
        title="Maximum input tokens",
        description="The maximum number of tokens the model that is fed into the model.")
    best_of: Optional[int] = Field(
        default=config.DEFAULT_BEST_OF,
        title="Best of",
        description="Number of completions produced by the model, which are used to prompt the reward model."
    )
    max_output_tokens: Optional[int] = Field(
        default=config.DEFAULT_MAX_OUTPUT_TOKENS,
        title="Maximum output tokens",
        description="The maximum number of tokens the model can generate in a single response.",
        options={
            "hidden": True
        }
    )

    _validation_errors: List[str] = PrivateAttr(default=[])

    def validate_currently_supported_format(self):
        # Validation is NOT done using pydantic validator for backward
        # compatibility
        self._validate_parameters()
        self._validate_presence_penalty()
        self._validate_frequency_penalty()
        self._validate_temperature()
        self._validate_top_k()
        self._validate_top_p()
        self._validate_min_p()
        self._validate_max_input_tokens()
        self._validate_max_output_tokens()
        self._validate_best_of()

        if self._validation_errors:
            error_messages = ', '.join(self._validation_errors)
            message = f"Generation Parameters validation failed with the following errors: {error_messages}"
            raise errors.ValidationError(message)

    def _validate_parameters(self):
        required_params = {'temperature', 'top_p', 'min_p', 'top_k', 'presence_penalty', 'frequency_penalty'}
        recognised_params = required_params.union({'max_input_tokens', 'stopping_words', 'best_of', 'max_output_tokens'})
        actual_params = set(self.dict(exclude_none=True).keys())

        # check there are no extra parameters
        extra_params = sorted(actual_params - recognised_params)
        if len(extra_params) > 0:
            msg = f'unrecognised generation parameters: {", ".join(extra_params)}'
            self._validation_errors.append(msg)

        # check there are no missing parameters
        missing_params = sorted(required_params - actual_params)
        if len(missing_params) > 0:
            msg = f'missing generation parameters: {", ".join(missing_params)}'
            self._validation_errors.append(msg)

    def _validate_presence_penalty(self):
        if self.presence_penalty is not None and not -2 <= self.presence_penalty <= 2:
            msg = f"`presence_penalty` must be in [-2, 2], got {self.presence_penalty}"
            self._validation_errors.append(msg)

    def _validate_frequency_penalty(self):
        if self.frequency_penalty is not None and not -2 <= self.frequency_penalty <= 2:
            msg = f"`frequency_penalty` must be in [-2, 2], got {self.frequency_penalty}"
            self._validation_errors.append(msg)

    def _validate_temperature(self):
        if self.temperature is not None and self.temperature < 0:
            self._validation_errors.append("`temperature` must be positive")

    def _validate_top_k(self):
        if self.top_k is not None and self.top_k <= 0:
            self._validation_errors.append("`top_k` must be greater than 0")

    def _validate_top_p(self):
        if self.top_p is not None and (self.top_p <= 0 or self.top_p > 1.0):
            self._validation_errors.append("`top_p` must be in (0, 1]")

    def _validate_min_p(self):
        if self.min_p is not None and (self.min_p < 0 or self.min_p > 1.0):
            self._validation_errors.append("`min_p` must be in [0, 1]")

    def _validate_best_of(self):
        if self.best_of is not None and (self.best_of <= 0 or self.best_of > 16):
            self._validation_errors.append("`best_of` must be in [1, 16]")

    def _validate_max_input_tokens(self):
        min_tokens = config.DEFAULT_MAX_INPUT_TOKENS
        max_tokens = 4096
        is_not_none = self.max_input_tokens is not None
        is_not_in_correct_range = not (min_tokens <= self.max_input_tokens <= max_tokens)
        if is_not_none and is_not_in_correct_range:
            msg = f"`max_input_tokens` must be in [{min_tokens}, {max_tokens}], got {self.max_input_tokens}"
            self._validation_errors.append(msg)

    def _validate_max_output_tokens(self):
        allowed_min = 32
        allowed_max = 112

        is_not_none = self.max_input_tokens is not None
        is_not_in_correct_range = not (allowed_min <= self.max_output_tokens <= allowed_max)

        if is_not_none and is_not_in_correct_range:
            msg = f"`max_output_tokens` must be in [{allowed_min}, {allowed_max}], got {self.max_output_tokens}"
            self._validation_errors.append(msg)


class FrontEndSubmissionRequest(BaseModel):
    class Config():
        title = 'Submit a model to Chaiverse'

    model_repo: str = Field(
        title="Model repository",
        description="HuggingFace repository hosting your model.",
        min_length=1
    )
    reward_repo: Optional[str] = Field(
        title="Reward model repository",
        description="HuggingFace repository hosting your reward model.",
        default=config.DEFAULT_REWARD_REPO
    )
    hf_auth_token: Optional[str] = Field(
        title="HuggingFace authentication token",
        description="A read-only HuggingFace token to access a private respository."
    )
    model_name: Optional[str] = Field(
        default=None,
        title="Model name",
        description="Set a custom name for your model."
    )
    generation_params: GenerationParams = Field(
        title="Generation Params",
        description="Set the parameters that control how your model samples tokens."
    )
    formatter: formatters.PromptFormatter = Field(
        title="Formatter",
        description="Provide a template to control how your model is prompted.",
        default=formatters.PygmalionFormatter()
    )
    reward_formatter: formatters.PromptFormatter = Field(
        title="Reward Formatter",
        description="Provide a template to control how your reward model is prompted.",
        default=formatters.PygmalionFormatter()
    )

    @validator("generation_params")
    def check_generation_params(cls, generation_params):
        generation_params.validate_currently_supported_format()
        return generation_params


class FrontEndBlendSubmissionRequest(BaseModel):
    submissions: List[str] = Field(..., description="submission_id for models to include in the blend.")
    model_name: Optional[str] = Field(None, description="name of your model.")


class ModelSubmitter:
    """
    Submits a model to the Guanaco service and exposes it to beta-testers on the Chai app.

    Attributes
    --------------
    developer_key : str
    verbose       : str - Print deployment logs

    Methods
    --------------
    submit(submission_params)
    Submits the model to the Guanaco service.

    Example usage:
    --------------
    submitter = ModelSubmitter(developer_key)
    submitter.submit(submission_params)
    """

    @auto_authenticate
    def __init__(self, developer_key=None, verbose=False):
        self.developer_key = developer_key
        self.verbose = verbose
        self._animation = self._spinner_animation_generator()
        self._progress = 0
        self._sleep_time = 0.5
        self._get_request_interval = int(10 / self._sleep_time)
        self._logs_cache = []

    def submit(self, submission_params):
        """
        Submits the model to the Guanaco service and wait for the deployment to finish.

        submission_params: dict
            model_repo: str - HuggingFace repo
            hf_auth_token (optional): str - A read-only token used to access model_repo
            generation_params: dict
                temperature: float
                top_p: float
                top_k: int
                repetition_penalty: float
            formatter (optional): PromptFormatter
            reward_formatter (optional): PromptFormatter
            model_name (optional): str - custom alias for your model
        """
        submission_params = submission_params.copy()
        submission_params = preprocess_submission(submission_params)
        return self._handle_submit(submit_model, submission_params)

    def submit_blend(self, submission_params):
        """
        Submits blend to the Guanaco service and wait for the deployment to finish.

        submission_params: dict
            submissions: list - submission_ids for the models in the blend
            model_name (optional): str - custom alias for your model
            override (optional): str - set parameter and formatter overrides for the sampled models
                {
                    "submission_id_v1": {
                        "generation_params": {
                            "temperature": 0.4
                        },
                        "formatter": {
                            "response_template": "{bot_name} (kind):"
                        }
                    }
                }
        """
        return self._handle_submit(submit_model_blend, submission_params)

    def submit_routed_blend(self, submission_params):
        return self._handle_submit(submit_model_routed_blend, submission_params)

    def submit_reward_blend(self, submission_params):
        return self._handle_submit(submit_model_reward_blend, submission_params)

    def _handle_submit(self, submission_func, submission_params):
        submission_response = submission_func(submission_params, self.developer_key)
        submission_id = submission_response.get('submission_id')
        self._print_submission_header(submission_id)
        status = self._wait_for_model_submission(submission_id)
        self._print_submission_result(status)
        self._progress = 0
        return submission_id

    def _wait_for_model_submission(self, submission_id):
        status = 'pending'
        while status not in {'deployed', 'failed', 'inactive'}:
            status = self._get_submission_status(submission_id)
            self._display_animation(status)
            time.sleep(self._sleep_time)
        return status

    def _get_submission_status(self, submission_id):
        self._progress += 1
        status = 'pending'
        if self._progress % self._get_request_interval == 0:
            model_info = get_model_info(submission_id, self.developer_key)
            self._print_latest_logs(model_info)
            status = model_info.get('status')
        return status

    def _spinner_animation_generator(self):
        animations = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        return itertools.cycle(animations)

    def _display_animation(self, status):
        text = f" {next(self._animation)} {status}..."
        if 'ipykernel' in sys.modules:
            display(text, display_id="animation")
        else:
            print(text, end='\r')

    def _print_submission_header(self, submission_id):
        utils.print_color(f'\nModel Submission ID: {submission_id}', 'green')
        print("Your model is being deployed to Chaiverse, please wait for approximately 10 minutes...")

    def _print_submission_result(self, status):
        success = status == 'deployed'
        text_success = 'Model successfully deployed!'
        text_failed = 'Model deployment failed, please seek help on our Discord channel'
        text = text_success if success else text_failed
        color = 'green' if success else 'red'
        print('\n')
        utils.print_color(f'\n{text}', color)

    def _print_latest_logs(self, model_info):
        if self.verbose:
            logs = model_info.get("logs", [])
            num_new_logs = len(logs) - len(self._logs_cache)
            new_logs = logs[-num_new_logs:] if num_new_logs else []
            self._logs_cache += new_logs
            for log in new_logs:
                message = utils.parse_log_entry(log)
                print(message)


def preprocess_submission(submission_params):
    if submission_params.get('formatter'):
        submission_params["formatter"] = submission_params["formatter"].dict()
    if submission_params.get("reward_formatter"):
        submission_params["reward_formatter"] = submission_params["reward_formatter"].dict()
    return submission_params


@auto_authenticate
def submit_model(model_submission: dict, developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.post(endpoint=config.SUBMISSION_ENDPOINT, json=model_submission)
    return response


@auto_authenticate
def submit_model_blend(model_submission: dict, developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.post(endpoint=config.BLEND_SUBMISSION_ENDPOINT, json=model_submission)
    return response


@auto_authenticate
def submit_model_routed_blend(model_submission: dict, developer_key=None):
    model_submission = _serialize_tagging_function(model_submission)
    http_client = SubmitterClient(developer_key)
    response = http_client.post(endpoint=config.ROUTED_BLEND_SUBMISSION_ENDPOINT, json=model_submission)
    return response


def _serialize_tagging_function(model_submission):
    function = model_submission.get("tagging_function")
    if function:
        model_submission["tagging_function"] = serialize_function(function)
    return model_submission


@auto_authenticate
def submit_model_reward_blend(model_submission: dict, developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.post(endpoint=config.REWARD_BLEND_SUBMISSION_ENDPOINT, json=model_submission)
    return response


@auto_authenticate
def get_model_info(submission_id, developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.get(endpoint=config.INFO_ENDPOINT, submission_id=submission_id)
    return response


@auto_authenticate
def evaluate_model(submission_id, developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.get(endpoint=config.EVALUATE_ENDPOINT, submission_id=submission_id)
    return response


@auto_authenticate
def get_my_submissions(developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.get(endpoint=config.ALL_SUBMISSION_STATUS_ENDPOINT)
    return response


@auto_authenticate
def search_submissions(developer_key=None, **kwargs):
    http_client = SubmitterClient(developer_key)
    response = http_client.get(endpoint=config.SEARCH_SUBMISSIONS_ENDPOINT, params=kwargs)
    return response


@auto_authenticate
def deactivate_model(submission_id, developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.get(endpoint=config.DEACTIVATE_ENDPOINT,submission_id=submission_id)
    print(response)
    return response


@auto_authenticate
def redeploy_model(submission_id, developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.get(endpoint=config.REDEPLOY_ENDPOINT, submission_id=submission_id)
    print(response)
    return response


@auto_authenticate
def teardown_model(submission_id, developer_key=None):
    http_client = SubmitterClient(developer_key)
    response = http_client.get(endpoint=config.TEARDOWN_ENDPOINT, submission_id=submission_id)
    print(response)
    return response


def get_all_historical_submissions(developer_key):
    return get_submissions(developer_key=developer_key)


def get_submissions(developer_key=None, date_range:Optional[DateRange]=None):
    params = {}
    if date_range and date_range.start_date:
        params['start_date'] = f'{date_range.start_date}'
    if date_range and date_range.end_date:
        params['end_date'] = f'{date_range.end_date}'
    client = SubmitterClient(developer_key)
    resp = client.get(LEADERBOARD_ENDPOINT, params=params)
    return resp
