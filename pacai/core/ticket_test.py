import edq.testing.unittest

import pacai.core.ticket

class TicketTest(edq.testing.unittest.BaseTest):
    """ Test ticket functionality. """

    def test_ordering_base(self):
        """ Test tickets are ordered properly. """

        # [(lower, higher), ...]
        test_cases = [
            (pacai.core.ticket.Ticket(0, 0, 0), pacai.core.ticket.Ticket(1, 0, 0)),
            (pacai.core.ticket.Ticket(0, 0, 0), pacai.core.ticket.Ticket(0, 1, 0)),
            (pacai.core.ticket.Ticket(0, 0, 0), pacai.core.ticket.Ticket(0, 0, 1)),

            (pacai.core.ticket.Ticket(0, 9, 9), pacai.core.ticket.Ticket(1, 0, 0)),
            (pacai.core.ticket.Ticket(0, 0, 9), pacai.core.ticket.Ticket(0, 1, 0)),

            (pacai.core.ticket.Ticket(-1, 0, 0), pacai.core.ticket.Ticket(1, 0, 0)),
        ]

        for (i, test_case) in enumerate(test_cases):
            (lower_ticket, higher_ticket) = test_case
            with self.subTest(msg = f"Case {i}: {lower_ticket} < {higher_ticket}"):
                self.assertTrue((lower_ticket.is_before(higher_ticket)))
