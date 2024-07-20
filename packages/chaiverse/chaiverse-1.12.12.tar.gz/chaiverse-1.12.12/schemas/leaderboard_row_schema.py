from datetime import datetime
import json
from typing import List, Optional, Union, Dict

from pydantic import BaseModel, Extra, Field, root_validator
from typing_extensions import Literal

from chaiverse import config
from chaiverse.lib.now import utcnow
from chaiverse.lib.pydantic_tools import get_fields_in_schema, UnionParser
from chaiverse.lib.date_tools import convert_to_us_pacific_date


class BaseLeaderboardRow(BaseModel, extra=Extra.allow):
    developer_uid: str
    submission_id: str
    model_name: Optional[str]
    model_group: Optional[str] = ""
    status: str
    timestamp: datetime = Field(default_factory=utcnow)

    # preference metrics
    num_battles: int = 0
    num_wins: int = 0
    celo_rating: Optional[float] = None

    # alignment scores
    propriety_score: Optional[float] = 0
    propriety_total_count: Optional[float] = 0

    @root_validator()
    def add_model_group(cls, values):
        if not values["model_group"]:
            values["model_group"] = values.get("model_repo", "")[:24]
        return values

    @property
    def display_name(self):
        name = self.model_name if self.model_name else self.submission_id
        return name

    @property
    def win_ratio(self):
        return self.num_wins / self.num_battles if self.num_battles > 0 else None

    @property
    def us_pacific_date(self):
        us_pacific_date = convert_to_us_pacific_date(self.timestamp).date()
        return us_pacific_date

    @property
    def ineligible_reason(self) -> Optional[str]:
        return None

    def can_auto_deactivate(self):
        is_deployed = self.status == 'deployed'
        has_enough_battles = self.num_battles >= config.AUTO_DEACTIVATION_MIN_NUM_BATTLES
        has_enough_propriety = self.propriety_total_count >= config.AUTO_DEACTIVATION_MIN_NUM_PROPRIETY
        return is_deployed and has_enough_battles and has_enough_propriety

    def all_fields_dict(self):
        fields = get_fields_in_schema(self.__class__)
        fields_dict = {key: getattr(self, key) for key in fields}
        return fields_dict

    def base_fields_dict(self):
        fields = BaseLeaderboardRow.__fields__.keys()
        fields_dict = {key: getattr(self, key) for key in fields}
        return fields_dict

    # pydantic 2.x implements model_dump. Existing dict() in pydantic 1.x doesn't serialize recursively
    def model_dump(self):
        return json.loads(self.json())


class BasicLeaderboardRow(BaseLeaderboardRow):
    submission_type: Literal['basic'] = Field(default='basic')
    model_repo: str
    model_architecture: Optional[str]
    reward_repo: str = None
    model_num_parameters: float = None
    best_of: int = 1
    max_input_tokens: int
    max_output_tokens: Optional[int]

    @property
    def language_model(self):
        return self.model_repo

    @property
    def reward_model(self):
        return self.reward_repo

    @property
    def model_size(self):
        size_gb = round(self.model_num_parameters / 1e9) if self.model_num_parameters else None
        size_gb = f'{size_gb}B'
        return size_gb

    @property
    def ineligible_reason(self) -> Optional[str]:
        reason = None
        if self.status != 'deployed' and self.num_battles < config.LEADERBOARD_STABLE_ELO_REQUIRED_BATTLES:
            reason = f'num_battles<{config.LEADERBOARD_STABLE_ELO_REQUIRED_BATTLES}'
        if self.status != 'deployed' and self.propriety_total_count < config.LEADERBOARD_REQUIRED_PROPRIETY:
            reason = f'propriety_total_count < {config.LEADERBOARD_REQUIRED_PROPRIETY}'
        if self.max_output_tokens != config.DEFAULT_MAX_OUTPUT_TOKENS and self.max_output_tokens != None:
            reason = f'max_output_tokens!={config.DEFAULT_MAX_OUTPUT_TOKENS}'
        if self.status not in ['inactive', 'deployed', 'torndown']:
            reason = 'model is not deployable'
        return reason


class BlendLeaderboardRow(BaseLeaderboardRow):
    submission_type: Literal['blend'] = Field(default='blend')
    submissions: List[str]

    @property
    def language_model(self):
        return ','.join(self.submissions)

    @property
    def reward_model(self):
        return 'random'

    @property
    def model_size(self):
        return 'n/a'


class RewardBlendLeaderboardRow(BaseLeaderboardRow):
    submission_type: Literal['reward_blend'] = Field(default='reward_blend')
    reward_repo: str

    submissions: List[str]
    num_samples: int

    @property
    def language_model(self):
        pseudo_language_model = ','.join(self.submissions)
        return pseudo_language_model

    @property
    def reward_model(self):
        return self.reward_repo

    @property
    def model_size(self):
        return 'n/a'


class TaggedSubmissionID(BaseModel):
    submission_id: str
    tags: Optional[List[str]] = None


class RoutedBlendLeaderboardRow(BaseLeaderboardRow):
    submission_type: Literal['routed_blend'] = Field(default='routed_blend')
    router: str
    tagged_submissions: List[TaggedSubmissionID]

    @property
    def language_model(self):
        tagged_submissions = []
        for tagged_submission in self.tagged_submissions:
            tags = '|'.join(tagged_submission.tags)
            tagged_submissions.append(f'{tagged_submission.submission_id}:{tags}')
        pseudo_language_model = ','.join(tagged_submissions)
        return pseudo_language_model

    @property
    def reward_model(self):
        return self.router

    @property
    def model_size(self):
        return 'n/a'


class BinaryRoutedBlendLeaderboardRow(BaseLeaderboardRow):
    submission_type: Literal['binary_routed_blend'] = Field(default='binary_routed_blend')
    router: str
    routing_config: Dict

    @property
    def language_model(self):
        default_submission = self.routing_config['default_submission']
        secondary_submission = self.routing_config['secondary_submission']
        threshold = self.routing_config['threshold']
        return '{} (threshold: {}), {}'.format(default_submission, threshold, secondary_submission)

    @property
    def reward_model(self):
        return self.router

    @property
    def model_size(self):
        return 'n/a'


LeaderboardRow = Union[
    BasicLeaderboardRow,
    BlendLeaderboardRow,
    RewardBlendLeaderboardRow,
    RoutedBlendLeaderboardRow,
]
