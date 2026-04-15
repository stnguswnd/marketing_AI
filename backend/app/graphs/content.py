from typing import List

from langgraph.graph import END, START, StateGraph

from app.graphs.state import ContentGraphState
from app.schemas.common import ContentStatus


def plan_content(state: ContentGraphState) -> ContentGraphState:
    notes = [
        "Target platform: %s." % state["platform"].value,
        "Goal: %s." % state["goal"].value.replace("_", " "),
    ]
    if state.get("tone"):
        notes.append("Tone: %s." % state["tone"])
    return {"strategy_notes": " ".join(notes)}


def generate_copy(state: ContentGraphState) -> ContentGraphState:
    country_label = {
        "JP": "Japan",
        "US": "United States",
        "CN": "China",
        "TW": "Taiwan",
        "HK": "Hong Kong",
    }[state["target_country"].value]
    title = "%s %s" % (country_label, state["goal"].value.replace("_", " "))
    body_parts = [state["input_brief"].strip()]
    if state.get("strategy_notes"):
        body_parts.append(state["strategy_notes"])
    if state.get("must_include"):
        body_parts.append("Must include: %s." % ", ".join(state["must_include"]))
    if state.get("must_avoid"):
        body_parts.append("Avoid: %s." % ", ".join(state["must_avoid"]))

    hashtags: List[str] = []
    for word in state.get("must_include", [])[:2]:
        clean = word.strip().replace(" ", "")
        if clean:
            hashtags.append("#%s" % clean)
    if not hashtags:
        hashtags = ["#global", "#marketing"]

    return {
        "title": title,
        "body": " ".join(body_parts),
        "hashtags": hashtags,
    }


def validate_copy(state: ContentGraphState) -> ContentGraphState:
    body = state.get("body", "")
    for phrase in state.get("must_avoid", []):
        body = body.replace(phrase, "").strip()
    missing = [phrase for phrase in state.get("must_include", []) if phrase not in body]
    if missing:
        body = "%s Must include enforced: %s." % (body, ", ".join(missing))
    return {
        "body": body,
        "validated": True,
        "status": state.get("status", ContentStatus.DRAFT),
    }


def build_content_graph():
    graph = StateGraph(ContentGraphState)
    graph.add_node("plan_content", plan_content)
    graph.add_node("generate_copy", generate_copy)
    graph.add_node("validate_copy", validate_copy)
    graph.add_edge(START, "plan_content")
    graph.add_edge("plan_content", "generate_copy")
    graph.add_edge("generate_copy", "validate_copy")
    graph.add_edge("validate_copy", END)
    return graph.compile()


content_graph = build_content_graph()


def run_content_graph(initial_state: ContentGraphState) -> ContentGraphState:
    return content_graph.invoke(initial_state)
