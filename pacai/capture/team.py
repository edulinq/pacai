import typing

import pacai.core.agentinfo

@typing.runtime_checkable
class TeamCreationFunction(typing.Protocol):
    """
    A function that can be used to create a capture team.
    """

    def __call__(self) -> list[pacai.core.agentinfo.AgentInfo]:
        """
        Get the agent infos used to construct a capture team.

        Standard capture usually uses two agents per team, but can technically support 10 total agents.
        If more agents than necessary are supplied, then the extra agents should be ignored.
        If fewer agent than necessary are supplied, then random agents should be used to fill out the rest of the team.
        """

def create_team_dummy() -> list[pacai.core.agentinfo.AgentInfo]:
    """
    Create a team with just dummy agents.
    """

    return [
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_DUMMY.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_DUMMY.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_DUMMY.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_DUMMY.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_DUMMY.long),
    ]

def create_team_random() -> list[pacai.core.agentinfo.AgentInfo]:
    """
    Create a team with just random agents.
    """

    return [
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_RANDOM.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_RANDOM.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_RANDOM.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_RANDOM.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_RANDOM.long),
    ]

def create_team_baseline() -> list[pacai.core.agentinfo.AgentInfo]:
    """
    Create a team with balanced defensive and offensive agents.
    """

    return [
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_CAPTURE_OFFENSIVE.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_CAPTURE_DEFENSIVE.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_CAPTURE_OFFENSIVE.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_CAPTURE_DEFENSIVE.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_CAPTURE_OFFENSIVE.long),
        pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_CAPTURE_DEFENSIVE.long),
    ]
