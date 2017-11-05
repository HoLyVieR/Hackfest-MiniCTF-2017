from flask import render_template, jsonify, Blueprint, redirect, url_for, request
from sqlalchemy.sql.expression import union_all

from CTFd.models import db, Teams, Solves, Awards, Challenges

from CTFd import utils

scoreboard = Blueprint('scoreboard', __name__)


def get_standings(admin=False, count=None):
    scores = db.session.query(
        Solves.teamid.label('teamid'),
        db.func.sum(Challenges.value).label('score'),
        db.func.max(Solves.id).label('id'),
        db.func.max(Solves.date).label('date')
    ).join(Challenges).group_by(Solves.teamid)

    awards = db.session.query(
        Awards.teamid.label('teamid'),
        db.func.sum(Awards.value).label('score'),
        db.func.max(Awards.id).label('id'),
        db.func.max(Awards.date).label('date')
    ).group_by(Awards.teamid)

    """
    Filter out solves and awards that are before a specific time point.
    """
    freeze = utils.get_config('freeze')
    if not admin and freeze:
        scores = scores.filter(Solves.date < utils.unix_time_to_utc(freeze))
        awards = awards.filter(Awards.date < utils.unix_time_to_utc(freeze))

    """
    Combine awards and solves with a union. They should have the same amount of columns
    """
    results = union_all(scores, awards).alias('results')

    """
    Sum each of the results by the team id to get their score.
    """
    sumscores = db.session.query(
        results.columns.teamid,
        db.func.sum(results.columns.score).label('score'),
        db.func.max(results.columns.id).label('id'),
        db.func.max(results.columns.date).label('date')
    ).group_by(results.columns.teamid).subquery()

    """
    Admins can see scores for all users but the public cannot see banned users.

    Filters out banned users.
    Properly resolves value ties by ID.

    Different databases treat time precision differently so resolve by the row ID instead.
    """
    if admin:
        standings_query = db.session.query(
            Teams.id.label('teamid'),
            Teams.name.label('name'),
            Teams.banned, sumscores.columns.score
        )\
            .join(sumscores, Teams.id == sumscores.columns.teamid) \
            .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
    else:
        standings_query = db.session.query(
            Teams.id.label('teamid'),
            Teams.name.label('name'),
            sumscores.columns.score
        )\
            .join(sumscores, Teams.id == sumscores.columns.teamid) \
            .filter(Teams.banned == False) \
            .order_by(sumscores.columns.score.desc(), sumscores.columns.id)

    """
    Only select a certain amount of users if asked.
    """
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()
    db.session.close()

    return standings


@scoreboard.route('/scoreboard')
def scoreboard_view():
    if utils.get_config('view_scoreboard_if_authed') and not utils.authed():
        return redirect(url_for('auth.login', next=request.path))
    if utils.hide_scores():
        return render_template('scoreboard.html', errors=['Scores are currently hidden'])
    standings = get_standings()
    return render_template('scoreboard.html', teams=standings, score_frozen=utils.is_scoreboard_frozen())


@scoreboard.route('/scores')
def scores():
    json = {'standings': []}
    if utils.get_config('view_scoreboard_if_authed') and not utils.authed():
        return redirect(url_for('auth.login', next=request.path))
    if utils.hide_scores():
        return jsonify(json)

    standings = get_standings()

    for i, x in enumerate(standings):
        json['standings'].append({'pos': i + 1, 'id': x.teamid, 'team': x.name, 'score': int(x.score)})
    return jsonify(json)


@scoreboard.route('/top/<int:count>')
def topteams(count):
    json = {'places': {}}
    if utils.get_config('view_scoreboard_if_authed') and not utils.authed():
        return redirect(url_for('auth.login', next=request.path))
    if utils.hide_scores():
        return jsonify(json)

    if count > 20 or count < 0:
        count = 10

    standings = get_standings(count=count)

    for i, team in enumerate(standings):
        solves = Solves.query.filter_by(teamid=team.teamid)
        awards = Awards.query.filter_by(teamid=team.teamid)

        freeze = utils.get_config('freeze')

        if freeze:
            solves = solves.filter(Solves.date < utils.unix_time_to_utc(freeze))
            awards = awards.filter(Awards.date < utils.unix_time_to_utc(freeze))

        solves = solves.all()
        awards = awards.all()

        json['places'][i + 1] = {
            'id': team.teamid,
            'name': team.name,
            'solves': []
        }
        for x in solves:
            json['places'][i + 1]['solves'].append({
                'chal': x.chalid,
                'team': x.teamid,
                'value': x.chal.value,
                'time': utils.unix_time(x.date)
            })
        for award in awards:
            json['places'][i + 1]['solves'].append({
                'chal': None,
                'team': award.teamid,
                'value': award.value,
                'time': utils.unix_time(award.date)
            })
        json['places'][i + 1]['solves'] = sorted(json['places'][i + 1]['solves'], key=lambda k: k['time'])
    return jsonify(json)
