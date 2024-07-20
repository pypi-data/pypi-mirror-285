"""
The LanceRAGTaskCreator.new() method creates a 3-Agent system that uses this agent.
It takes a LanceDocChatAgent instance as argument, and adds two more agents:
- LanceQueryPlanAgent, which is given the LanceDB schema in LanceDocChatAgent,
and based on this schema, for a given user query, creates a Query Plan
using the QueryPlanTool, which contains a filter, a rephrased query,
and a dataframe_calc.
- QueryPlanCritic, which is given the LanceDB schema in LanceDocChatAgent,
 and gives feedback on the Query Plan and Result using the QueryPlanFeedbackTool.

The LanceRAGTaskCreator.new() method sets up the given LanceDocChatAgent and
QueryPlanCritic as sub-tasks of the LanceQueryPlanAgent's task.

Langroid's built-in task orchestration ensures that:
- the LanceQueryPlanAgent reformulates the plan based
    on the QueryPlanCritics's feedback,
- LLM deviations are corrected via tools and overrides of ChatAgent methods.
"""

import logging

from langroid.agent.special.lance_tools import (
    QueryPlanAnswerTool,
)
from langroid.agent.task import Task
from langroid.mytypes import Entity
from langroid.utils.constants import NO_ANSWER

from ..lance_doc_chat_agent import LanceDocChatAgent
from .critic_agent import (
    QueryPlanCritic,
    QueryPlanCriticConfig,
)
from .query_planner_agent import (
    LanceQueryPlanAgent,
    LanceQueryPlanAgentConfig,
)

logger = logging.getLogger(__name__)


def run_lance_rag_task(
    query: str,
    agent: LanceDocChatAgent,
    interactive: bool = True,
) -> str:
    """
    Add a LanceFilterAgent to the LanceDocChatAgent,
    set up the corresponding Tasks, connect them,
    and return the top-level query_plan_task.
    """
    doc_agent_name = "LanceRAG"
    critic_name = "QueryPlanCritic"
    query_plan_agent_config = LanceQueryPlanAgentConfig(
        critic_name=critic_name,
        doc_agent_name=doc_agent_name,
        doc_schema=agent._get_clean_vecdb_schema(),
    )
    query_plan_agent_config.set_system_message()

    query_planner = LanceQueryPlanAgent(query_plan_agent_config)
    query_plan_task = Task(
        query_planner,
        interactive=interactive,
        restart=False,
        done_if_response=[Entity.AGENT],
    )
    # TODO - figure out how to define the fns so we avoid re-creating
    # agents in each invocation. Right now we are defining the fn
    # inside this context, which may not be great.

    rag_task = Task(
        agent,
        name="LanceRAG",
        restart=True,  # default; no need to accumulate dialog
        interactive=False,
        done_if_response=[Entity.LLM],  # done when non-null response from LLM
        done_if_no_response=[Entity.LLM],  # done when null response from LLM
    )

    critic_config = QueryPlanCriticConfig(
        doc_schema=agent._get_clean_vecdb_schema(),
    )
    critic_config.set_system_message()

    critic_agent = QueryPlanCritic(critic_config)
    critic_task = Task(
        critic_agent,
        interactive=False,
        restart=True,  # default; no need to accumulate dialog
    )

    no_answer = False
    feedback = None
    i = 0
    while i := i + 1 < 5:
        # query, feedback (QueryPlanFeedbackTool) => ChatDocument[QueryPlanTool]
        if feedback is not None and feedback.suggested_fix != "":
            prompt = f"""
                A Critic has seen your Query Plan and the Answer, and has given the 
                following feedback. Take it into account and re-generate your Query Plan
                for the QUERY:
                
                QUERY: {query}
                FEEDBACK: {feedback.feedback}
                SUGGESTED FIX: {feedback.suggested_fix}
                """
        elif no_answer:
            prompt = f"There was a {NO_ANSWER} response; try a different query plan"
        else:
            prompt = query

        while True:
            plan_doc = query_plan_task.run(prompt)
            if len(plan_doc.tool_messages) > 0:
                break
            # forgot to use QueryPlanTool
            prompt = """You forgot to use the `query_plan` tool/function. Try again."""

        # TODO if plan_doc does NOT have a QueryPlan, remind the agent

        # ChatDocument with QueryPlanTool => ChatDocument with answer
        rag_answer_doc = rag_task.run(plan_doc)

        if rag_answer_doc is None:
            rag_answer_doc = rag_task.agent.create_llm_response(NO_ANSWER)
        # QueryPlan, answer => QueryPlanAnswerTool
        plan_answer_tool = QueryPlanAnswerTool(
            plan=plan_doc.tool_messages[0].plan,
            answer=rag_answer_doc.content,
        )
        # QueryPlanAnswerTool => ChatDocument[QueryPlanAnswerTool]
        plan_answer_doc = agent.create_agent_response(tool_messages=[plan_answer_tool])

        # ChatDocument[QueryPlanAnswerTool] => ChatDocument[QueryPlanFeedbackTool]
        feedback_doc = critic_task.run(plan_answer_doc)
        # ChatDocument[QueryPlanFeedbackTool] => QueryPlanFeedbackTool
        feedback = feedback_doc.tool_messages[0]  # QueryPlanFeedbackTool
        no_answer = NO_ANSWER in rag_answer_doc.content
        if feedback.suggested_fix == "" and not no_answer:
            break

    # query_plan_task.add_sub_task([critic_task, rag_task])
    return rag_answer_doc.content
