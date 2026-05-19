"""Smoke tests."""

from starlord.core.agent import Agent


def test_agent_smoke():
    agent = Agent()
    response = agent.handle_input("hello")
    assert "Intent=" in response
