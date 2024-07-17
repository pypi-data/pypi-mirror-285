from typing import List, Literal, Optional

from chaiverse.http_client import SubmitterClient
from chaiverse.cli_utils.login_cli import auto_authenticate
from chaiverse.schemas import Competition
from chaiverse import config


@auto_authenticate
def get_competitions(status: Optional[Literal['submitting', 'evaluating']]=None, developer_key=None) -> List[Competition]:
    submitter_client = SubmitterClient(developer_key=developer_key)
    response = submitter_client.get(config.COMPETITIONS_ENDPOINT, params=dict(status=status))
    competitions = [Competition(**competition) for competition in response['competitions']]
    return competitions


def get_competition_by_id(competition_id: str, developer_key: str) -> Competition:
    submitter_client = SubmitterClient(developer_key=developer_key)
    url = config.COMPETITION_ENDPOINT.format(competition_id=competition_id)
    response = submitter_client.get(url)
    competition = Competition(**response)
    return competition


def create_competition(competition: Competition, developer_key: str=None):
    submitter_client = SubmitterClient(developer_key=developer_key)
    url = config.COMPETITIONS_ENDPOINT
    competition_id = submitter_client.post(url, json=competition.model_dump())
    return competition_id


def update_competition(competition_id: str, competition: Competition, developer_key: str=None):
    submitter_client = SubmitterClient(developer_key=developer_key)
    url = config.COMPETITION_ENDPOINT.format(competition_id=competition_id)
    competition = submitter_client.put(url, json=competition.model_dump())
    competition = Competition(**competition)
    return competition


def enroll_submission(submission_id, competition_id=None, developer_key=None):
    submission_ids = add_or_remove_enrolled_competition_ids(
        submission_ids_to_add=[submission_id],
        submission_ids_to_remove=[],
        competition_id=competition_id,
        developer_key=developer_key
    )
    return submission_ids


def withdraw_submission(submission_id, competition_id=None, developer_key=None):
    submission_ids = add_or_remove_enrolled_competition_ids(
        submission_ids_to_add=[],
        submission_ids_to_remove=[submission_id],
        competition_id=competition_id,
        developer_key=developer_key
    )
    return submission_ids


def add_or_remove_enrolled_competition_ids(submission_ids_to_add, submission_ids_to_remove, competition_id=None, developer_key=None):
    competition = _get_competition_for_enrollment(competition_id)
    submitter_client = SubmitterClient(developer_key=developer_key)
    for submission_id in submission_ids_to_remove:
        url = config.COMPETITION_ENROLLED_SUBMISSION_IDS_ENDPOINT.format(submission_id=submission_id, competition_id=competition.competition_id)
        submission_ids = submitter_client.delete(url)
        print(f'Withdrawn {submission_id} from {competition.display_name}.')
    for submission_id in submission_ids_to_add:
        url = config.COMPETITION_ENROLLED_SUBMISSION_IDS_ENDPOINT.format(submission_id=submission_id, competition_id=competition.competition_id)
        submission_ids = submitter_client.post(url)
        print(f'Enrolled {submission_id} into {competition.display_name}.')
    return submission_ids


def _get_competition_for_enrollment(competition_id=None, developer_key=None):
    if competition_id is None:
        competitions = get_competitions(status='submitting')
        assert competitions, 'No competition in submitting status'
        competition = competitions[0]
    else:
        competition = get_competition_by_id(competition_id, developer_key=developer_key)
    return competition
