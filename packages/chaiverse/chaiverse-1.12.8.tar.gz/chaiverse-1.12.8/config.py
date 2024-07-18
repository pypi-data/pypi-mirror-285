BASE_SUBMITTER_URL = "https://guanaco-submitter.chai-research.com"
BASE_FEEDBACK_URL = "https://guanaco-feedback.chai-research.com"
BASE_PROMETHEUS_URL = "https://guanaco-prometheus.chai-research.com"
BASE_AUTH_URL = "https://auth.chaiverse.com"

LATEST_LEADERBOARD_ENDPOINT = "/latest_leaderboard"
LEADERBOARDS_ENDPOINT = "/leaderboards"
LEADERBOARD_AUTO_DEACTIVATE = '/auto_deactivate'
LEADERBOARD_ENDPOINT = "/leaderboard"
CHAT_ENDPOINT = "/models/{submission_id}/chat"
FEEDBACK_SUMMARY_ENDPOINT = "/feedback"
FEEDBACK_ENDPOINT = "/feedback/{submission_id}"

SUBMISSION_ENDPOINT = "/models/submit"
BLEND_SUBMISSION_ENDPOINT = "/models/submit_blend"
REWARD_BLEND_SUBMISSION_ENDPOINT = "/models/submit_reward_blend"
ROUTED_BLEND_SUBMISSION_ENDPOINT = "/models/submit_routed_blend"
ALL_SUBMISSION_STATUS_ENDPOINT = "/models/"
SEARCH_SUBMISSIONS_ENDPOINT = "/models/search"
INFO_ENDPOINT = "/models/{submission_id}"
DEACTIVATE_ENDPOINT = "/models/{submission_id}/deactivate"
REDEPLOY_ENDPOINT = "/models/{submission_id}/redeploy"
EVALUATE_ENDPOINT = "/models/{submission_id}/evaluate"
TEARDOWN_ENDPOINT = "/models/{submission_id}/teardown"
FEED_ENDPOINT = "/feed"
USER_FEED_ENDPOINT = "/users/{username}/feed"

COMPETITIONS_ENDPOINT = '/competitions'
COMPETITION_ENDPOINT = '/competitions/{competition_id}'
COMPETITION_ENROLLED_SUBMISSION_IDS_ENDPOINT = '/competitions/{competition_id}/enrolled_submission_ids/{submission_id}'

USAGE_METRICS_ENDPOINT = '/{submission_id}/usage-metrics'
LATENCY_METRICS_ENDPOINT = '/{submission_id}/latency-metrics'

DEFAULT_BEST_OF = 4
DEFAULT_REWARD_REPO = "ChaiML/reward_gpt2_medium_preference_24m_e2"
DEFAULT_MAX_INPUT_TOKENS = 512
DEFAULT_MAX_OUTPUT_TOKENS = 64

AUTO_DEACTIVATION_MIN_NUM_BATTLES = 5000
AUTO_DEACTIVATION_MIN_NUM_PROPRIETY = 5000
AUTO_DEACTIVATION_MAX_ELO_RATING = 1000
AUTO_DEACTIVATION_MIN_RANK = 1

LEADERBOARD_STABLE_ELO_REQUIRED_BATTLES = 5000
LEADERBOARD_REQUIRED_PROPRIETY = 5000

ELO_REQUIRED_BATTLES = 1000
ELO_BASE_SUBMISSION_ID = 'mistralai-mixtral-8x7b-_3473_v11'
ELO_BASE_RATING = 1114


def get_elo_base_submission_id():
    return ELO_BASE_SUBMISSION_ID


def get_elo_base_rating():
    return ELO_BASE_RATING
