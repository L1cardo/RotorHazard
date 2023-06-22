''' Class ranking method: By final position, favoring later heats in class '''

import logging
import RHUtils
from eventmanager import Evt
from RHRace import StartBehavior
from Results import RaceClassRankMethod

logger = logging.getLogger(__name__)

def register_handlers(args):
    if 'register_fn' in args:
        for method in discover():
            args['register_fn'](method)

def initialize(**kwargs):
    if 'events' in kwargs:
        kwargs['events'].on(Evt.CLASS_RANK_INITIALIZE, 'classrank_register_heat_position', register_handlers, {}, 75)

def rank_heat_pos(rhapi, race_class, _args):
    heats = rhapi.db.heats_by_class(race_class.id)

    leaderboard = []
    ranked_pilots = []
    rank_pos = 1

    for heat in reversed(heats):
        heat_result = rhapi.db.heat_results(heat)
        heat_leaderboard = heat_result[heat_result['meta']['primary_leaderboard']]

        for line in heat_leaderboard:
            if line['pilot_id'] not in ranked_pilots:
                leaderboard.append({
                    'pilot_id': line['pilot_id'],
                    'callsign': line['callsign'],
                    'team_name': line['team_name'],
                    'heat': heat.display_name(),
                    'heat_rank': line['position'],
                    'position': rank_pos
                })

                ranked_pilots.append(line['pilot_id'])
                rank_pos += 1

    meta = {
        'rank_fields': [{
            'name': 'heat',
            'label': "Heat"
        },{
            'name': 'heat_rank',
            'label': "Position"
        }]
    }

    return leaderboard, meta

def discover(*_args, **_kwargs):
    # returns array of methods with default arguments
    return [
        RaceClassRankMethod(
            'last_heat_position',
            'Last Heat Position',
            rank_heat_pos,
            None,
            None
        )
    ]
