import edq.testing.unittest

import pacai.core.board
import pacai.core.gamestate
import pacai.core.ticket
import pacai.search.position

class GameStateTest(edq.testing.unittest.BaseTest):
    """ Test different game state functionalities. """

    def test_get_agent_position_base(self):
        """ Test getting agent positions. """

        board = pacai.core.board.load_path('classic-test')
        tickets = {
            0: pacai.core.ticket.Ticket(0, 0, 0),
            1: pacai.core.ticket.Ticket(1, 0, 0),
        }

        state = pacai.core.gamestate.GameState(
                seed = 4,
                board = board,
                agent_index = 0,
                tickets = tickets)

        agent_0_position = pacai.core.board.Position(8, 1)
        agent_1_position = pacai.core.board.Position(2, 2)

        agent_positions_expected = {
            0: agent_0_position,
            1: agent_1_position,
        }
        agent_positions_actual = state.get_agent_positions()
        self.assertJSONDictEqual(agent_positions_expected, agent_positions_actual)

        self.assertEqual(agent_0_position, state.get_agent_position(), 'default agent')
        self.assertEqual(agent_0_position, state.get_agent_position(0), 'agent 0')

        self.assertEqual(agent_1_position, state.get_agent_position(1), 'agent 1')
