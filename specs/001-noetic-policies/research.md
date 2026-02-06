# Research: Noetic Policies Package

**Date**: 2026-02-05
**Feature**: Build the noetic-policies package
**Branch**: 001-noetic-policies

## Overview

This document captures technical research findings for implementing the noetic-policies package, addressing key technical decisions and unknowns identified during planning.

---

## 1. Graph Analysis Library Selection

### Decision: NetworkX

**Chosen Library**: NetworkX 3.6.1+

**Rationale**:
- **Pure Python**: Zero compilation complexity, trivial installation (`pip install networkx`)
- **Type Hint Support**: Full support via `types-networkx` package for mypy strict mode compliance
- **Performance**: Meets all requirements for 1000+ node graphs
  - Reachability (BFS): O(V+E), ~10-50ms for 1000 nodes
  - Strongly Connected Components: O(V+E), ~20-100ms for 1000 nodes
  - Simple Cycles: Fast for graphs with reasonable cycle count
- **Recent Benchmarks** (January 2026): NetworkX is 2.5-4.6× *faster* than graph-tool for basic traversal operations
- **Pydantic Integration**: Straightforward with `arbitrary_types_allowed`
- **Developer Experience**: Excellent documentation, Pythonic API, active maintenance

**Alternatives Considered**:
- **igraph**: 8-10× faster for complex metrics, but requires C library compilation, less Pythonic API, limited type hints
- **graph-tool**: Fastest for complex algorithms (35× faster betweenness centrality), but C++ based, 2.5-4.6× slower for traversal, complex installation

**Conclusion**: For noetic-policies use case (reachability, deadlock detection, goal state verification), NetworkX provides optimal balance of performance, developer experience, and constitutional compliance (type safety, observability).

### Key Algorithms

#### Reachability Analysis
```python
import networkx as nx

# Primary: nx.has_path(G, source, target) - O(V+E) using BFS
# Alternative: nx.descendants(G, source) - get all reachable states at once
```

#### Unreachable State Detection
```python
def find_unreachable_states(G: nx.DiGraph, initial_state: str) -> set[str]:
    reachable = {initial_state} | nx.descendants(G, initial_state)
    all_states = set(G.nodes())
    return all_states - reachable
```

#### Deadlock Detection
```python
# Approach: Find terminal strongly connected components (SCCs with no exits)
sccs = nx.strongly_connected_components(G)  # O(V+E) using Tarjan's algorithm
# Terminal SCCs without goal states = deadlocks
```

### Integration Pattern
```python
from pydantic import BaseModel
import networkx as nx

class PolicyStateGraph(BaseModel):
    initial_state: str
    goal_states: set[str]
    states: list[str]
    transitions: list[StateTransition]

    _graph: nx.DiGraph | None = None

    model_config = {"arbitrary_types_allowed": True}

    def build_graph(self) -> nx.DiGraph:
        if self._graph is not None:
            return self._graph
        G = nx.DiGraph()
        G.add_nodes_from(self.states)
        for trans in self.transitions:
            G.add_edge(trans.from_state, trans.to_state)
        self._graph = G
        return G
```

### Dependencies
- `networkx>=3.6.1`
- `types-networkx>=3.6.1` (for type checking)

**Sources**:
- [NetworkX for Python — A Practical Guide](https://medium.com/@jainsnehasj6/networkx-for-python-a-practical-guide-to-cycle-detection-and-connectivity-algorithms-f6025c73915d)
- [Benchmark of popular graph/network packages v2](https://www.timlrx.com/blog/benchmark-of-popular-graph-network-packages-v2)
- [Performance Comparison of graph-tool and NetworkX](https://figshare.com/articles/conference_contribution/_b_Performance_Comparison_of_graph-tool_and_NetworkX_on_Web_Graph_Domain_Subgraphs_b_/31155247)

---

## 2. Testing Strategy for Static Analysis Validation

### Framework: pytest + Hypothesis + pytest-benchmark

**Core Testing Approach**:
1. **Unit Tests**: Individual validation rules (parser, validator, graph analyzer)
2. **Integration Tests**: End-to-end validation workflows
3. **Property-Based Tests**: Hypothesis for exploring edge cases
4. **Performance Tests**: pytest-benchmark for <1s fast mode requirement

### Hypothesis Property-Based Testing Patterns

**Custom Strategy for Policy Generation**:
```python
from hypothesis import strategies as st

@st.composite
def cel_expressions(draw):
    variable = draw(st.sampled_from(["balance", "amount", "timestamp"]))
    operator = draw(st.sampled_from([">", "<", ">=", "<=", "=="]))
    value = draw(st.integers(min_value=0, max_value=1000))
    return f"{variable} {operator} {value}"

@st.composite
def valid_policies(draw):
    num_states = draw(st.integers(min_value=2, max_value=10))
    states = draw(st.lists(state_names, min_size=num_states, unique=True))
    return {
        "version": "1.0",
        "constraints": [...],
        "state_graph": {...}
    }
```

**Property Tests**:
```python
from hypothesis import given

@given(valid_policies())
def test_valid_policies_always_parse(policy):
    result = PolicyParser.parse_dict(policy)
    assert result is not None

@given(valid_policies())
def test_thorough_mode_includes_fast_mode_checks(policy):
    fast_result = validator.validate_dict(policy, mode="fast")
    thorough_result = validator.validate_dict(policy, mode="thorough")

    if not fast_result.is_valid:
        assert not thorough_result.is_valid
```

### Error Message Quality Testing (SC-003: 90% Fixable Without Docs)

**Structured Error Format**:
```python
@dataclass
class ValidationError:
    code: str                    # e.g., "E001"
    message: str                 # Human-readable description
    line_number: Optional[int]
    column_number: Optional[int]
    severity: str                # "error", "warning", "info"
    fix_suggestion: Optional[str]
    documentation_url: Optional[str]
```

**Quality Checklist**:
- ✅ Location (line/column number)
- ✅ Problem description
- ✅ Expected value
- ✅ Fix suggestion

**Testing Pattern**:
```python
def test_error_messages_contain_fix_suggestions(self):
    policy_yaml = """
    version: "1.0"
    # Missing constraints section
    """

    result = validator.validate_yaml(policy_yaml)
    error = result.errors[0]

    # Check error quality
    assert "constraints" in error.message.lower()
    assert "add" in error.message.lower() or "include" in error.message.lower()
    assert error.line_number is not None
```

### OpenTelemetry Testing (Without External Dependencies)

**Strategy**: Use `InMemorySpanExporter` from OpenTelemetry SDK

**Fixture Setup**:
```python
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

@pytest.fixture
def span_exporter():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    yield exporter
    exporter.clear()
```

**Testing Pattern**:
```python
def test_validation_creates_span(span_exporter, tracer):
    validator = PolicyValidator(tracer=tracer)
    result = validator.validate_yaml(policy_yaml)

    spans = span_exporter.get_finished_spans()
    assert len(spans) > 0

    validation_span = next(s for s in spans if s.name == "policy.validate")
    assert validation_span.status.is_ok == result.is_valid
```

### Performance Testing (Fast Mode <1 Second)

**Primary Tool**: pytest-benchmark

**Pattern**:
```python
def test_fast_mode_under_one_second(benchmark):
    validator = PolicyValidator()

    result = benchmark(validator.validate_yaml, policy_yaml, mode="fast")

    assert benchmark.stats.mean < 1.0, \
        f"Fast mode took {benchmark.stats.mean:.3f}s, expected <1s"
```

**Scaling Tests**:
```python
@pytest.mark.parametrize("num_states,max_time_ms", [
    (5, 200),
    (10, 400),
    (20, 800),
    (50, 1000),
])
def test_fast_mode_scaling_limits(benchmark, num_states, max_time_ms):
    policy = create_policy(num_states)
    validator = PolicyValidator()
    benchmark(validator.validate_dict, policy, mode="fast")

    assert benchmark.stats.mean * 1000 < max_time_ms
```

### Dual-Mode Testing

**Parametrized Fixtures**:
```python
@pytest.fixture(params=["fast", "thorough"])
def validation_mode(request):
    return request.param

def test_validation_works_in_all_modes(validation_mode, policy):
    result = validator.validate_dict(policy, mode=validation_mode)
    assert result is not None
```

**Mode-Specific Markers**:
```python
@pytest.mark.fast_mode
def test_fast_mode_time_constraint(self):
    # Test fast mode <1s requirement
    pass

@pytest.mark.thorough_mode
def test_thorough_mode_deadlock_detection(self):
    # Test thorough mode detects deadlocks
    pass
```

### Testing Dependencies

**Essential**:
- `pytest>=8.0` - Core testing framework
- `pytest-cov>=4.1` - Coverage measurement (80% requirement)
- `hypothesis>=6.98` - Property-based testing
- `pytest-benchmark>=4.0` - Performance testing
- `opentelemetry-sdk>=1.22` - Observability testing

**Recommended**:
- `pytest-xdist>=3.5` - Parallel test execution
- `pytest-timeout>=2.2` - Prevent hanging tests
- `pytest-watch>=4.2` - TDD watch mode

### pytest Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-ra",
    "--strict-markers",
    "--cov=noetic_policies",
    "--cov-report=term-missing",
    "--cov-fail-under=80",  # Constitution requirement
]

markers = [
    "fast_mode: Tests for fast validation mode",
    "thorough_mode: Tests for thorough validation mode",
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests",
    "property: Property-based tests",
    "performance: Performance tests",
]
```

**Sources**:
- [pytest documentation](https://docs.pytest.org/)
- [Python Testing Best Practices 2026](https://pytest-with-eric.com/introduction/python-unit-testing-best-practices/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [pytest-benchmark guide](https://pytest-benchmark.readthedocs.io/)
- [OpenTelemetry Python test examples](https://github.com/open-telemetry/opentelemetry-python/blob/main/opentelemetry-sdk/tests/trace/export/test_in_memory_span_exporter.py)

---

## 3. Additional Technical Decisions

### CEL (Common Expression Language) Library

**Decision**: Use `celpy` library

**Rationale**:
- Pure Python implementation of CEL
- Deterministic evaluation (constitutional requirement)
- Type checking support
- Active maintenance
- Compatible with Python 3.11+

**Integration**:
```python
from celpy import celtypes, celparser, celast, Runner

def evaluate_constraint(expr: str, context: dict) -> bool:
    env = celast.Environment()
    ast = env.compile(expr)
    program = env.program(ast)
    runner = Runner(program)
    return runner.evaluate(context)
```

**Dependency**: `celpy>=0.20`

### Policy Format Versioning

**Decision**: Semantic versioning embedded in policy files

**Format**:
```yaml
version: "1.0"  # MAJOR.MINOR format
name: policy_name
# ...
```

**Migration Strategy** (from clarification Q4):
- Version detection: Parse `version` field
- Support current version + 1 previous
- Optional automatic migration (configurable)
- Deprecation warnings for old versions

### OpenTelemetry Integration

**Decision**: Comprehensive logging with OpenTelemetry (from clarification Q3)

**Implementation**:
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Validation with tracing
tracer = trace.get_tracer(__name__)

def validate_policy(policy):
    with tracer.start_as_current_span("policy.validate") as span:
        span.set_attribute("policy.version", policy.version)
        span.set_attribute("policy.num_states", len(policy.states))

        # Validation logic with nested spans
        with tracer.start_as_current_span("policy.validate.schema"):
            validate_schema(policy)

        # ...
```

**Dependencies**:
- `opentelemetry-api>=1.22`
- `opentelemetry-sdk>=1.22`

---

## 4. Summary of Technical Context Resolution

| Unknown | Research Finding | Decision |
|---------|-----------------|----------|
| Graph analysis library | NetworkX vs igraph vs graph-tool | **NetworkX 3.6.1+** - optimal for use case, pure Python, excellent type hints |
| Testing patterns for validation | pytest + Hypothesis + pytest-benchmark | **Comprehensive suite**: property-based, performance, observability testing |
| Property-based testing approach | Hypothesis strategies for policies | **Custom strategies** for CEL expressions, state graphs, valid/invalid policies |
| OpenTelemetry testing | InMemorySpanExporter | **No external dependencies** - use SDK's in-memory exporter |
| Performance testing | pytest-benchmark vs custom | **pytest-benchmark** - precise timing, statistical analysis, regression tracking |
| Error message testing | Quality checklist | **4-element checklist**: location, problem, expected, suggestion |

All NEEDS CLARIFICATION items from Technical Context have been resolved with research-backed decisions.

---

## References

### Graph Analysis
- NetworkX documentation: https://networkx.org/documentation/stable/
- NetworkX benchmark comparison (2026): https://www.timlrx.com/blog/benchmark-of-popular-graph-network-packages-v2
- NetworkX algorithms: https://networkx.org/documentation/stable/reference/algorithms/

### Testing
- pytest documentation: https://docs.pytest.org/
- Hypothesis documentation: https://hypothesis.readthedocs.io/
- pytest-benchmark: https://pytest-benchmark.readthedocs.io/
- OpenTelemetry Python testing: https://github.com/open-telemetry/opentelemetry-python

### CEL
- CEL specification: https://github.com/google/cel-spec
- celpy library: https://github.com/cloud-custodian/cel-python

### Standards
- OpenTelemetry specification: https://opentelemetry.io/docs/specs/otel/
- Semantic versioning: https://semver.org/
