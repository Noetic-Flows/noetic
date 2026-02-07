"""State graph analysis using NetworkX (T068-T072)."""

import networkx as nx

from noetic_policies.models import GoalState, GraphAnalysisResult, TemporalBounds
from noetic_policies.models.state_graph import StateGraph


class GraphAnalyzer:
    """
    Analyzes state graphs for reachability, deadlocks, and costs.

    Uses NetworkX for graph algorithms (per research.md).
    Implements FR-004, FR-005, FR-007.
    """

    def __init__(self):
        """Initialize graph analyzer."""
        pass

    def analyze(
        self,
        state_graph: StateGraph,
        initial: str,
        goals: list[GoalState],
        policy_temporal_bounds: TemporalBounds | None = None,
    ) -> GraphAnalysisResult:
        """
        Perform complete graph analysis.

        Args:
            state_graph: State graph to analyze
            initial: Initial state name
            goals: Goal states with scoring and temporal bounds
            policy_temporal_bounds: Global temporal bounds

        Returns:
            GraphAnalysisResult with analysis findings
        """
        # Build NetworkX graph
        G = self._build_networkx_graph(state_graph)

        # T069: Find unreachable states
        unreachable = self.find_unreachable_states(state_graph, initial)

        # T070: Detect deadlocks
        deadlocks = self.detect_deadlocks(state_graph)

        # T071: Verify goal reachability
        goal_names = {g.name for g in goals}
        goal_reachable = self.verify_goal_reachable(state_graph, initial, goal_names)

        # T071a: Compute goal costs (Dijkstra's)
        goal_costs = self._compute_goal_costs(G, initial, goals)

        # T071b: Compute minimum steps (BFS)
        goal_min_steps = self._compute_goal_min_steps(G, initial, goals)

        # T071c: Check temporal feasibility
        temporally_infeasible = self._check_temporal_feasibility(
            goal_min_steps, goals, policy_temporal_bounds
        )

        return GraphAnalysisResult(
            unreachable_states=unreachable,
            deadlock_sccs=deadlocks,
            goal_reachable=goal_reachable,
            goal_costs=goal_costs,
            goal_min_steps=goal_min_steps,
            temporally_infeasible_goals=temporally_infeasible,
        )

    def _build_networkx_graph(self, state_graph: StateGraph) -> nx.DiGraph:
        """Build NetworkX directed graph from state graph."""
        G = nx.DiGraph()

        # Add all states as nodes
        for state in state_graph.states:
            G.add_node(state.name)

        # Add transitions as edges with cost weights
        for state in state_graph.states:
            for transition in state.transitions:
                G.add_edge(
                    state.name,
                    transition.to,
                    weight=transition.cost,  # For Dijkstra's
                )

        return G

    def find_unreachable_states(
        self, state_graph: StateGraph, initial: str
    ) -> set[str]:
        """
        Find states not reachable from initial state.

        Args:
            state_graph: State graph to analyze
            initial: Initial state name

        Returns:
            Set of unreachable state names
        """
        G = self._build_networkx_graph(state_graph)

        # Get all reachable states from initial
        try:
            reachable = {initial} | nx.descendants(G, initial)
        except nx.NetworkXError:
            reachable = {initial}

        # All states minus reachable = unreachable
        all_states = {state.name for state in state_graph.states}
        return all_states - reachable

    def detect_deadlocks(self, state_graph: StateGraph) -> list[set[str]]:
        """
        Detect deadlock cycles in state graph.

        A deadlock is a strongly connected component (SCC) with no outgoing edges.

        Args:
            state_graph: State graph to analyze

        Returns:
            List of deadlock SCCs (each is a set of state names)
        """
        G = self._build_networkx_graph(state_graph)

        # Find all strongly connected components
        sccs = list(nx.strongly_connected_components(G))

        # A component is a deadlock if it has no outgoing edges
        deadlocks = []
        for scc in sccs:
            # Check if this SCC has any edges leaving it
            has_exit = False
            for node in scc:
                for successor in G.successors(node):
                    if successor not in scc:
                        has_exit = True
                        break
                if has_exit:
                    break

            # If no exit and more than just initial state, it's a deadlock
            if not has_exit and len(scc) > 1:
                deadlocks.append(scc)

        return deadlocks

    def verify_goal_reachable(
        self, state_graph: StateGraph, initial: str, goals: set[str]
    ) -> bool:
        """
        Check if any goal state is reachable from initial state.

        Args:
            state_graph: State graph to analyze
            initial: Initial state name
            goals: Goal state names

        Returns:
            True if at least one goal is reachable
        """
        G = self._build_networkx_graph(state_graph)

        for goal in goals:
            if nx.has_path(G, initial, goal):
                return True

        return False

    def _compute_goal_costs(
        self, G: nx.DiGraph, initial: str, goals: list[GoalState]
    ) -> dict[str, float]:
        """
        Compute minimum cost to reach each goal using Dijkstra's algorithm.

        Args:
            G: NetworkX graph
            initial: Initial state name
            goals: Goal states

        Returns:
            Dictionary mapping goal name to minimum cost
        """
        goal_costs = {}

        for goal in goals:
            try:
                # Use Dijkstra's algorithm with transition costs as weights
                cost = nx.dijkstra_path_length(G, initial, goal.name, weight="weight")
                goal_costs[goal.name] = cost
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                # Goal is unreachable
                pass

        return goal_costs

    def _compute_goal_min_steps(
        self, G: nx.DiGraph, initial: str, goals: list[GoalState]
    ) -> dict[str, int]:
        """
        Compute minimum number of steps (transitions) to reach each goal.

        Uses BFS for unweighted shortest path.

        Args:
            G: NetworkX graph
            initial: Initial state name
            goals: Goal states

        Returns:
            Dictionary mapping goal name to minimum steps
        """
        goal_min_steps = {}

        for goal in goals:
            try:
                # BFS shortest path (unweighted)
                steps = nx.shortest_path_length(G, initial, goal.name)
                goal_min_steps[goal.name] = steps
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                # Goal is unreachable
                pass

        return goal_min_steps

    def _check_temporal_feasibility(
        self,
        goal_min_steps: dict[str, int],
        goals: list[GoalState],
        policy_bounds: TemporalBounds | None,
    ) -> list[str]:
        """
        Check which goals are temporally infeasible.

        A goal is infeasible if minimum steps to reach it exceeds max_steps.

        Args:
            goal_min_steps: Minimum steps to each goal
            goals: Goal states with temporal bounds
            policy_bounds: Policy-level temporal bounds

        Returns:
            List of infeasible goal names
        """
        infeasible = []

        for goal in goals:
            min_steps = goal_min_steps.get(goal.name)
            if min_steps is None:
                # Unreachable - handled separately
                continue

            # Check goal-level max_steps
            if goal.temporal_bounds and goal.temporal_bounds.max_steps is not None:
                if min_steps > goal.temporal_bounds.max_steps:
                    infeasible.append(goal.name)
                    continue

            # Check policy-level max_steps
            if policy_bounds and policy_bounds.max_steps is not None:
                if min_steps > policy_bounds.max_steps:
                    infeasible.append(goal.name)

        return infeasible
