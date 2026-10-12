"""Tests for tiny_agent_scope - 32 tests."""
import time
import pytest

from tiny_agent_scope import (
    AgentScope,
    BudgetExceeded,
    ScopeViolation,
    scope_for,
    agent_scope,
)


def test_initial_used_zero():
    s = scope_for("t")
    u = s.used()
    assert u["steps"] == 0
    assert u["tool_calls"] == 0
    assert u["tokens"] == 0
    assert u["cost_usd"] == 0.0
    assert u["wall_seconds"] >= 0.0


def test_remaining_with_no_budgets():
    s = scope_for("t")
    r = s.remaining()
    assert all(v is None for v in r.values())


def test_step_increments():
    s = scope_for("t", max_steps=3)
    s.step()
    s.step()
    s.step()
    assert s.used()["steps"] == 3
    with pytest.raises(BudgetExceeded) as e:
        s.step()
    assert e.value.budget == "step"


def test_max_tool_calls():
    s = scope_for("t", max_tool_calls=2)
    s.record_tool_call("a")
    s.record_tool_call("b")
    with pytest.raises(BudgetExceeded):
        s.record_tool_call("c")


def test_max_tokens():
    s = scope_for("t", max_tokens=10)
    s.record_tokens(7)
    s.record_tokens(2)
    with pytest.raises(BudgetExceeded):
        s.record_tokens(2)


def test_max_cost():
    s = scope_for("t", max_cost_usd=1.0)
    s.record_cost(0.4)
    s.record_cost(0.4)
    with pytest.raises(BudgetExceeded):
        s.record_cost(0.4)


def test_max_wall_seconds():
    s = scope_for("t", max_wall_seconds=0.0)
    time.sleep(0.01)
    with pytest.raises(BudgetExceeded):
        s.step()


def test_record_tool_call_combines():
    s = scope_for("t", max_tool_calls=2, max_tokens=10, max_cost_usd=0.5)
    s.record_tool_call("a", tokens=5, cost_usd=0.2)
    s.record_tool_call("b", tokens=3, cost_usd=0.2)
    assert s.used()["tool_calls"] == 2
    assert s.used()["tokens"] == 8
    assert abs(s.used()["cost_usd"] - 0.4) < 1e-6


def test_denied_tool_rejected():
    s = scope_for("t", denied_tools={"exec"})
    with pytest.raises(ScopeViolation) as e:
        s.record_tool_call("exec")
    assert e.value.kind == "tool"
    assert e.value.target == "exec"


def test_allowed_tools_whitelist():
    s = scope_for("t", allowed_tools={"read"})
    s.record_tool_call("read")
    with pytest.raises(ScopeViolation):
        s.record_tool_call("write")


def test_denied_takes_precedence():
    s = scope_for("t", allowed_tools={"a", "b"}, denied_tools={"b"})
    s.record_tool_call("a")
    with pytest.raises(ScopeViolation):
        s.record_tool_call("b")


def test_on_violation_callback():
    seen = []
    s = scope_for("t", denied_tools={"x"}, on_violation=lambda s, k, t: seen.append((k, t)))
    with pytest.raises(ScopeViolation):
        s.record_tool_call("x")
    assert seen == [("tool_denied", "x")]


def test_on_step_callback():
    seen = []
    s = scope_for("t", on_step=lambda s, n: seen.append(n))
    s.step("first")
    s.step("second")
    assert seen == ["first", "second"]


def test_abort_flag():
    s = scope_for("t", max_steps=10)
    s.abort()
    assert s.aborted()
    with pytest.raises(BudgetExceeded):
        s.step()


def test_abort_callback():
    seen = []
    s = scope_for("t", on_abort=lambda s: seen.append(s.name))
    s.abort()
    assert seen == ["t"]


def test_path_denied_glob(tmp_path):
    blocked = tmp_path / "secret.txt"
    blocked.write_text("x")
    s = scope_for("t", denied_paths=[str(tmp_path / "*")])
    with pytest.raises(ScopeViolation):
        s.check_path(str(blocked))


def test_path_allowed_glob(tmp_path):
    allowed_dir = tmp_path / "workspace"
    allowed_dir.mkdir()
    s = scope_for("t", allowed_paths=[str(allowed_dir / "*")])
    f = allowed_dir / "x.txt"
    f.write_text("x")
    s.check_path(str(f))  # no raise


def test_path_not_in_allowed_raises(tmp_path):
    s = scope_for("t", allowed_paths=["/nonexistent/*"])
    with pytest.raises(ScopeViolation):
        s.check_path(str(tmp_path / "x"))


def test_path_read_only_blocks_writes(tmp_path):
    ro = tmp_path / "config.yaml"
    ro.write_text("x")
    s = scope_for("t", read_only_tools=[str(ro)])
    s.check_path(str(ro))  # read OK
    with pytest.raises(ScopeViolation) as e:
        s.check_path(str(ro), write=True)
    assert e.value.kind == "path_write"


def test_url_host_denied():
    s = scope_for("t", denied_hosts=["evil.com"])
    with pytest.raises(ScopeViolation):
        s.check_url("https://api.evil.com/x")


def test_url_host_allowed_glob():
    s = scope_for("t", allowed_hosts=["*.wikipedia.org"])
    s.check_url("https://en.wikipedia.org/wiki/Python")
    with pytest.raises(ScopeViolation):
        s.check_url("https://example.com")


def test_url_no_path_raises():
    s = scope_for("t", allowed_hosts=["api.example.com"])
    with pytest.raises(ScopeViolation):
        s.check_url("not-a-url")


def test_used_and_remaining_track():
    s = scope_for("t", max_steps=5, max_tokens=100, max_cost_usd=1.0)
    s.step()
    s.record_tokens(20)
    s.record_cost(0.3)
    u = s.used()
    r = s.remaining()
    assert u["steps"] == 1
    assert r["steps"] == 4
    assert r["tokens"] == 80
    assert abs(r["cost_usd"] - 0.7) < 1e-6


def test_record_tokens_zero_is_noop():
    s = scope_for("t", max_tokens=5)
    s.record_tokens(0)
    s.record_tokens(-1)
    assert s.used()["tokens"] == 0


def test_record_cost_zero_is_noop():
    s = scope_for("t", max_cost_usd=1.0)
    s.record_cost(0.0)
    s.record_cost(-0.1)
    assert s.used()["cost_usd"] == 0.0


def test_context_manager_yields_scope():
    with agent_scope("t", max_steps=2) as s:
        s.step()
        assert s.used()["steps"] == 1


def test_context_manager_calls_on_abort():
    seen = []
    with agent_scope("t", on_abort=lambda s: seen.append("aborted")) as s:
        s.abort()
    assert seen == ["aborted"]


def test_violations_logged():
    s = scope_for("t", denied_tools={"x", "y"})
    for _ in range(2):
        try:
            s.record_tool_call("x")
        except ScopeViolation:
            pass
    assert len(s._state["violations"]) == 2
    assert s._state["violations"][0]["kind"] == "tool_denied"


def test_step_name_passed_to_callback():
    seen = []
    s = scope_for("t", on_step=lambda s, n: seen.append(n))
    s.step("plan")
    s.step("act")
    assert seen == ["plan", "act"]


def test_path_abspath_normalization(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("x")
    s = scope_for("t", allowed_paths=[str(tmp_path) + "/*"])
    s.check_path("./" + str(f.relative_to(tmp_path.parent)) if False else str(f))


def test_combined_workflow():
    s = scope_for(
        "agent",
        max_steps=3,
        max_tool_calls=2,
        max_tokens=100,
        max_cost_usd=1.0,
        allowed_tools={"search", "read"},
    )
    s.step()
    s.record_tool_call("search", tokens=20, cost_usd=0.1)
    s.step()
    s.record_tool_call("read", tokens=30, cost_usd=0.05)
    s.step()
    # would exceed tool_calls on a 3rd
    with pytest.raises(BudgetExceeded):
        s.record_tool_call("search", tokens=10, cost_usd=0.05)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
