from langgraph.graph import END, START, StateGraph

from app.graphs.state import ReviewGraphState
from app.schemas.common import ReviewSensitivity


HIGH_RISK_WORDS = ("refund", "complaint", "angry", "bad", "worst", "불편", "아쉬", "환불")


def assess_review_sensitivity(state: ReviewGraphState) -> ReviewGraphState:
    lowered = state["review_text"].lower()
    if state["rating"] <= 2 or any(word in lowered for word in HIGH_RISK_WORDS):
        sensitivity = ReviewSensitivity.HIGH
    elif state["rating"] == 3:
        sensitivity = ReviewSensitivity.MEDIUM
    else:
        sensitivity = ReviewSensitivity.LOW
    return {
        "sensitivity": sensitivity,
        "escalated": sensitivity == ReviewSensitivity.HIGH,
    }


def build_reply_draft(state: ReviewGraphState) -> ReviewGraphState:
    sensitivity = state["sensitivity"]
    if sensitivity == ReviewSensitivity.HIGH:
        reply = "불편을 드려 죄송합니다. 말씀 주신 내용을 확인하고 개선하겠습니다."
    elif sensitivity == ReviewSensitivity.MEDIUM:
        reply = "소중한 의견 감사합니다. 더 나은 경험을 위해 확인하겠습니다."
    else:
        reply = "방문해 주셔서 감사합니다. 다음에도 좋은 경험을 드릴 수 있도록 노력하겠습니다."
    return {"reply_draft": reply}


def build_review_graph():
    graph = StateGraph(ReviewGraphState)
    graph.add_node("assess_review_sensitivity", assess_review_sensitivity)
    graph.add_node("build_reply_draft", build_reply_draft)
    graph.add_edge(START, "assess_review_sensitivity")
    graph.add_edge("assess_review_sensitivity", "build_reply_draft")
    graph.add_edge("build_reply_draft", END)
    return graph.compile()


review_graph = build_review_graph()


def run_review_graph(initial_state: ReviewGraphState) -> ReviewGraphState:
    return review_graph.invoke(initial_state)
