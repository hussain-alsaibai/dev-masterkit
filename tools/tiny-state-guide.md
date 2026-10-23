# tiny-state Guide

**Repo:** [hussain-alsaibai/tiny-state](https://github.com/hussain-alsaibai/tiny-state)  
**Deps:** 0 (stdlib-only) | **Last verified:** 2026-10-23

> Zero-dependency finite state machine for Python. Built for AI agents and workflows.

## What it does

A minimal but complete FSM implementation for modeling agent workflows, multi-step processes, and stateful systems — all without external dependencies.

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_state import StateMachine,
state, transition` with a `StateMachine` base class. **The class is named `FSM`
and there is an `AsyncFSM` too.** Verified against upstream `tiny_state.py`:

```
__all__ = ['FSM', 'AsyncFSM', 'state', 'transition', 'guard', 'Context', 'Transition']
```

Also present: `StateType`, `guard`, `Context`, `Transition`.

## When to use

- **Agent workflow modeling** — define states (idle, thinking, acting, waiting) and transitions
- **Multi-step processes** — order fulfillment, onboarding flows, async job state machines
- **Protocol implementation** — model network protocols, API state machines
- **Testing stateful systems** — deterministic FSM for reproducible testing

## Key patterns

```python
from tiny_state import FSM, state, transition

class AgentFSM(FSM):
    idle = state(initial=True)
    thinking = state()
    acting = state()
    done = state()

    @transition(idle, thinking)
    def start(self): pass

    @transition(thinking, acting)
    def plan_ready(self): pass

agent = AgentFSM()
agent.start()      # idle -> thinking
agent.plan_ready() # thinking -> acting
```

`AsyncFSM` provides the same shape for `async def` transitions.
`guard(...)` attaches a predicate to a transition so it only fires when the
condition holds.

## Related

- `tiny-workflow` — DAG orchestrator with retry and approval gates
- `tiny-eventbus` — pub/sub for state change notifications
- `tiny-chain` — LLM chain that can be driven by state transitions
