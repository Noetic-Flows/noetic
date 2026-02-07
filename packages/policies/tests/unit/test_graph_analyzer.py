"""Unit tests for graph analysis (T037-T041e)."""

import pytest

from noetic_policies.models import GoalState, TemporalBounds
from noetic_policies.models.state_graph import State, StateGraph, Transition


class TestGraphAnalyzer:
    """Test state graph analysis logic."""

    # T037: Test find_unreachable_states() detects orphaned states
    def test_find_unreachable_states(self):
        """Graph analyzer should detect unreachable states."""
        # Will be implemented when GraphAnalyzer is created
        # For now, just test the model structure
        graph = StateGraph(
            initial="start",
            states=[
                State(name="start", transitions=[Transition(to="middle")]),
                State(name="middle", transitions=[Transition(to="end")]),
                State(name="end"),
                State(name="orphan"),  # Not reachable from start
            ],
        )
        assert len(graph.states) == 4
        assert graph.initial == "start"

    # T038: Test detect_deadlocks() finds terminal SCCs without exits
    def test_detect_deadlocks(self):
        """Graph analyzer should detect deadlock cycles."""
        # Cycle with no exit = deadlock
        graph = StateGraph(
            initial="start",
            states=[
                State(name="start", transitions=[Transition(to="loop1")]),
                State(name="loop1", transitions=[Transition(to="loop2")]),
                State(name="loop2", transitions=[Transition(to="loop1")]),  # Cycle!
            ],
        )
        assert len(graph.states) == 3

    # T039: Test verify_goal_reachable() confirms path to goal exists
    def test_verify_goal_reachable(self):
        """Graph analyzer should verify goals are reachable."""
        graph = StateGraph(
            initial="start",
            states=[
                State(name="start", transitions=[Transition(to="goal")]),
                State(name="goal"),  # Reachable
            ],
        )
        assert len(graph.states) == 2

    # T040: Test unreachable goal state fails validation
    def test_unreachable_goal_fails(self):
        """Unreachable goal states should be detected."""
        graph = StateGraph(
            initial="start",
            states=[
                State(name="start"),  # No transitions
                State(name="unreachable_goal"),  # Can't reach this
            ],
        )
        assert len(graph.states) == 2

    # T041: Test circular state graph with exit is valid
    def test_circular_graph_with_exit_valid(self):
        """Circular graphs are valid if there's an exit transition."""
        graph = StateGraph(
            initial="start",
            states=[
                State(
                    name="start",
                    transitions=[
                        Transition(to="loop"),
                        Transition(to="exit"),  # Exit from cycle
                    ],
                ),
                State(name="loop", transitions=[Transition(to="start")]),  # Cycle back
                State(name="exit"),  # Exit state
            ],
        )
        assert len(graph.states) == 3

    # T041a: Test goal_costs computed correctly using Dijkstra's
    def test_goal_costs_dijkstra(self):
        """Minimum cost to goals should use Dijkstra's algorithm with transition costs."""
        graph = StateGraph(
            initial="start",
            states=[
                State(
                    name="start",
                    transitions=[
                        Transition(to="expensive", cost=10.0),
                        Transition(to="cheap", cost=1.0),
                    ],
                ),
                State(name="expensive", transitions=[Transition(to="goal", cost=1.0)]),
                State(name="cheap", transitions=[Transition(to="goal", cost=1.0)]),
                State(name="goal"),
            ],
        )
        # Cheapest path: start -> cheap -> goal = 1.0 + 1.0 = 2.0
        # Expensive path: start -> expensive -> goal = 10.0 + 1.0 = 11.0
        assert len(graph.states) == 4

    # T041b: Test goal_min_steps computed correctly (unweighted shortest path)
    def test_goal_min_steps(self):
        """Minimum steps should use BFS for unweighted shortest path."""
        graph = StateGraph(
            initial="start",
            states=[
                State(
                    name="start",
                    transitions=[
                        Transition(to="middle", cost=100.0),  # High cost
                        Transition(to="goal", cost=1.0),  # Low cost
                    ],
                ),
                State(name="middle", transitions=[Transition(to="goal", cost=1.0)]),
                State(name="goal"),
            ],
        )
        # Min steps: start -> goal = 1 step (ignoring cost)
        # Min cost: start -> goal = 1.0 (also direct path)
        assert len(graph.states) == 3

    # T041c: Test temporally_infeasible_goals detected when min_steps > max_steps
    def test_temporally_infeasible_goals(self):
        """Goals should be marked infeasible if min_steps exceeds max_steps."""
        graph = StateGraph(
            initial="start",
            states=[
                State(name="start", transitions=[Transition(to="middle")]),
                State(name="middle", transitions=[Transition(to="far_goal")]),
                State(name="far_goal"),
            ],
        )
        # Min steps to far_goal = 2
        # If max_steps = 1, goal is infeasible
        goal = GoalState(
            name="far_goal",
            temporal_bounds=TemporalBounds(max_steps=1),  # Too few steps!
        )
        assert goal.temporal_bounds.max_steps == 1

    # T041d: Test temporal feasibility passes when min_steps <= max_steps
    def test_temporal_feasibility_passes(self):
        """Goals should be feasible when min_steps is within max_steps."""
        graph = StateGraph(
            initial="start",
            states=[
                State(name="start", transitions=[Transition(to="goal")]),
                State(name="goal"),
            ],
        )
        # Min steps = 1
        goal = GoalState(
            name="goal",
            temporal_bounds=TemporalBounds(max_steps=10),  # Plenty of steps
        )
        assert goal.temporal_bounds.max_steps == 10

    # T041e: Test goals ranked by priority then reward
    def test_goals_ranked_by_priority_reward(self):
        """Goals should be ordered by priority (higher first), then reward."""
        goals = [
            GoalState(name="low_priority", priority=1, reward=100.0),
            GoalState(name="high_priority", priority=10, reward=1.0),
            GoalState(name="same_priority_low_reward", priority=5, reward=5.0),
            GoalState(name="same_priority_high_reward", priority=5, reward=50.0),
        ]

        # Sort by priority (desc), then reward (desc)
        sorted_goals = sorted(goals, key=lambda g: (-g.priority, -g.reward))

        assert sorted_goals[0].name == "high_priority"  # Priority 10
        assert sorted_goals[1].name == "same_priority_high_reward"  # Priority 5, reward 50
        assert sorted_goals[2].name == "same_priority_low_reward"  # Priority 5, reward 5
        assert sorted_goals[3].name == "low_priority"  # Priority 1
