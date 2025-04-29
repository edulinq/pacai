import pacai.core.ticket
import pacai.test.base

class TicketTest(pacai.test.base.BaseTest):
    def test_ordering_base(self):
        # [(lower, higher), ...]
        test_cases = [
            (pacai.core.ticket.Ticket(0, 0, 0), pacai.core.ticket.Ticket(1, 0, 0)),
            (pacai.core.ticket.Ticket(0, 0, 0), pacai.core.ticket.Ticket(0, 1, 0)),
            (pacai.core.ticket.Ticket(0, 0, 0), pacai.core.ticket.Ticket(0, 0, 1)),

            (pacai.core.ticket.Ticket(0, 9, 9), pacai.core.ticket.Ticket(1, 0, 0)),
            (pacai.core.ticket.Ticket(0, 0, 9), pacai.core.ticket.Ticket(0, 1, 0)),

            (pacai.core.ticket.Ticket(-1, 0, 0), pacai.core.ticket.Ticket(1, 0, 0)),
        ]

        for i in range(len(test_cases)):
            (lower_ticket, higher_ticket) = test_cases[i]
            with self.subTest(msg = f"Case {i}: {lower_ticket} < {higher_ticket}"):
                self.assertTrue((lower_ticket < higher_ticket))
