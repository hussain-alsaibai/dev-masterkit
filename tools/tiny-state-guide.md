# tiny-state Guide

**Repo:** [hussain-alsaibai/tiny-state](https://github.com/hussain-alsaibai/tiny-state)  
**Deps:** 0 (stdlib-only) | **Last verified:** 2026-07-24

> Zero-dependency finite state machine for Python. Built for AI agents and workflows.

## What it does

A minimal but complete FSM implementation for modeling agent workflows, multi-step processes, and stateful systems — all without external dependencies.

## When to use

- **Agent workflow modeling** — define states (idle, thinking, acting, waiting) and transitions
- **Multi-step processes** — order fulfillment, onboarding flows, async job state machines
- **Protocol implementation** — model network protocols, API state machines
- **Testing stateful systems** — deterministic FSM for reproducible testing

## Key patterns

```python
from tiny_state import StateMachine, state, transition

class AgentFSM(StateMachine):
    idle = state(initial=True)
    thinking = state()
    acting = state()
    done = state()

    @transition(idle, thinking)
    def start(self): pass

    @transition(thinking, acting)
    def plan_ready(self): pass

agent = AgentFSM()
agent.start()      # idle → thinking
agent.plan_ready() # thinking → acting
```

## Related

- `tiny-workflow` — DAG orchestrator with retry and approval gates
- `tiny-eventbus` — pub/sub for state change notifications
- `tiny-chain` — LLM chain that can be driven by state transitions
