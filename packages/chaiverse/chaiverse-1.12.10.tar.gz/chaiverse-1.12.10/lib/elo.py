import logging
from math import log10

# a player that never lost a game will have elo score of 1e30 and elo_rating of 9999
# a player that never win a game will have elo score of 1e-30 and elo_rating of 0
HIGHEST_ELO_SCORE = 1e30
LOWEST_ELO_SCORE = 1e-30
HIGHEST_ELO_RATING = 9999
LOWEST_ELO_RATING = 0

# set elo_rating_error_bar = max_elo_rating_diff * ELO_RATING_ERROR_BAR_MULTIPLIER
ELO_RATING_ERROR_BAR_MULTIPLIER = 10

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_mle_elo_scores(initial_elo_scores, wins_dict, elo_rating_error_bar=0.01):
    """
    Calculate elo_scores using MLE algorithm.
    MLE refers to maximum likelyhood estimation. The elo_score here is proportional to win odd, and
      elo_rating = elo_base + elo_scale * log10(elo_score)

    Let's say there are two models, i, j, and a third model k as arbitrary chosen baseline, and
    let's call p(i>j) is probability that i wins j:
      elo_score(i) = win_odd(i,k) * 2
      elo_score(k) = 1
      win_odd(i,j) = win_odd(i,k) * win_odd(k,j)  -> this is required to be true if score exists
      win_odd(i,j) = p(i>j) / (1-p(i>j))
      p(i>j) = elo_score(i) / (elo_score(i) + elo_score(j))

    Reference of the algorithm
    https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model
    https://jmlr.org/papers/volume24/22-1086/22-1086.pdf

    Different algorithms converges at different speed. The algorithm used here is proposed in 2023
    in the paper referenced. It is 100x faster than previous Zermelo. The implementation below is also
    efficient with sparse matrix.
    """
    new_elo_scores = initial_elo_scores
    rating_error = elo_rating_error_bar
    for iteration in range(500):
        prev_elo_scores = new_elo_scores.copy()
        for player in new_elo_scores.keys():
            new_elo_scores[player] = _get_updated_elo_score(new_elo_scores, player, wins_dict)
        rating_error = _get_elo_rating_error_bar(new_elo_scores, prev_elo_scores)
        logging.info('refining elo iteration=%d rating_error=%s', iteration, rating_error)

        if rating_error < elo_rating_error_bar and iteration > 10:
            # run at least 10 times to ensure the elo will eventually converge
            break

    if rating_error >= elo_rating_error_bar:
        raise ValueError('elo failed to converage with error={rating_error}')
    new_elo_scores = _normalize_elo_scores(new_elo_scores)
    return new_elo_scores


def _get_updated_elo_score(new_elo_scores, competitor_id, wins_dict):
    numerator = 0
    denominator = 0
    for opponent_id in wins_dict.get(competitor_id, {}).keys():
        score_sum = new_elo_scores[competitor_id] + new_elo_scores[opponent_id]
        numerator += wins_dict[competitor_id][opponent_id] * new_elo_scores[opponent_id] / score_sum
    for opponent_id in wins_dict.keys():
        score_sum = new_elo_scores[competitor_id] + new_elo_scores[opponent_id]
        denominator += wins_dict[opponent_id].get(competitor_id, 0) / score_sum
    score = LOWEST_ELO_SCORE
    if numerator > 0:
        score = numerator / denominator if denominator > 0 else HIGHEST_ELO_SCORE
    return score


def _get_elo_rating_error_bar(new_elo_scores, elo_scores):
    new_elo_ratings = get_elo_ratings(new_elo_scores, 0.5, 1000)
    elo_ratings = get_elo_ratings(elo_scores, 0.5, 1000)
    elo_ratings_diffs = [
        abs(new_elo_ratings[player] - elo_ratings[player]) for player in elo_ratings.keys()
        if LOWEST_ELO_RATING < new_elo_ratings[player] < HIGHEST_ELO_RATING and
        LOWEST_ELO_RATING < elo_ratings[player] < HIGHEST_ELO_RATING
    ]
    max_elo_rating_diff = max(elo_ratings_diffs, default=0)
    return max_elo_rating_diff * ELO_RATING_ERROR_BAR_MULTIPLIER


def _normalize_elo_scores(scores_dict):
    scores_to_average = [
        score for score in scores_dict.values()
        if 0 < score < HIGHEST_ELO_SCORE
    ]
    normalized = scores_dict
    if len(scores_to_average):
        average_elo_score = sum(scores_to_average) / len(scores_to_average)
        normalized = {
            player: score / average_elo_score if LOWEST_ELO_SCORE < score < HIGHEST_ELO_SCORE else score
            for player, score in scores_dict.items()
        }
    return normalized


def get_elo_ratings(scores, elo_base_score, elo_base_rating):
    elo_ratings = {
        player: get_elo_rating(score, elo_base_score, elo_base_rating)
        for player, score in scores.items()
    }
    return elo_ratings


def get_elo_rating(score, elo_base_score, elo_base_rating):
    if score <= LOWEST_ELO_SCORE:
        rating = LOWEST_ELO_RATING
    elif score >= HIGHEST_ELO_SCORE:
        rating = HIGHEST_ELO_RATING
    else:
        rating = 400 * log10(score / elo_base_score) + elo_base_rating
        rating = max(rating, LOWEST_ELO_RATING)
        rating = min(rating, HIGHEST_ELO_RATING)
        # different environment has different precision, and round to 2 digits is well
        # beyond necessary precision without incur mismatch in test
        rating = round(rating, 2)
    return rating
