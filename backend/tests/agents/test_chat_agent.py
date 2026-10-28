import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from pmo.agents import chat_agent
from pmo.agents.chat_agent import GREETING_REPLY, REFUSAL, ChatUnavailable, ask


class FakeLLM(GenericFakeChatModel):
    seen: list = []

    def bind_tools(self, tools, **kw):
        return self

    def _generate(self, messages, *a, **kw):
        self.seen.append(list(messages))
        return super()._generate(messages, *a, **kw)


def tool_call(name, args=None, i=0):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args or {}, "id": f"c{i}"}])


def fake(*msgs, scope="ON_TOPIC"):
    return FakeLLM(messages=iter((AIMessage(content=scope), *msgs)), seen=[])


def test_ask_returns_answer_and_tools_used(items):
    llm = fake(tool_call("get_kpis", {"project": "Project A"}), AIMessage(content="1 blocked"))
    r = ask(items, "how many blocked?", [], "Project A", llm=llm)
    assert r == {"answer": "1 blocked", "tools_used": ["get_kpis"]}


def test_ask_raises_when_no_llm(items, monkeypatch):
    monkeypatch.setattr(chat_agent, "_get_llm", lambda: None)
    with pytest.raises(ChatUnavailable):
        ask(items, "hi", [])


def test_history_trimmed_to_last_10(items):
    llm = fake(AIMessage(content="ok"))
    hist = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"} for i in range(30)]
    ask(items, "new", hist, llm=llm)
    msgs = llm.seen[1]
    assert [m.content for m in msgs[1:]] == [f"m{i}" for i in range(20, 30)] + ["new"]


def test_system_prompt_mentions_selected_project(items):
    llm = fake(AIMessage(content="ok"))
    ask(items, "hi", [], "Project B", llm=llm)
    assert "Project B" in llm.seen[1][0].content


def test_tool_call_limit_stops_runaway_loop(items):
    llm = FakeLLM(messages=iter([AIMessage(content="ON_TOPIC"), *(tool_call("list_projects", i=i) for i in range(100))]), seen=[])
    r = ask(items, "loop", [], llm=llm)
    assert "couldn't finish" in r["answer"] and len(r["tools_used"]) <= 6


def test_off_topic_is_refused_without_running_agent(items):
    llm = fake(scope="OFF_TOPIC")
    assert ask(items, "write me a poem", [], llm=llm) == {"answer": REFUSAL, "tools_used": []}
    assert len(llm.seen) == 1


def test_greeting_gets_friendly_reply_without_running_agent(items):
    llm = fake(scope="GREETING")
    assert ask(items, "hi", [], llm=llm) == {"answer": GREETING_REPLY, "tools_used": []}
    assert len(llm.seen) == 1


def test_scope_check_sees_history_for_follow_ups(items):
    llm = fake(AIMessage(content="ok"))
    ask(items, "and who owns it?", [{"role": "user", "content": "what is blocked?"}], llm=llm)
    assert "what is blocked?" in llm.seen[0][1].content


def test_scope_check_failure_lets_message_through(items):
    class Flaky(FakeLLM):
        calls: int = 0

        def invoke(self, *a, **kw):
            if not self.calls:
                self.calls = 1
                raise RuntimeError("boom")
            return super().invoke(*a, **kw)

    llm = Flaky(messages=iter([AIMessage(content="1 blocked")]), seen=[])
    assert ask(items, "how many blocked?", [], llm=llm)["answer"] == "1 blocked"
