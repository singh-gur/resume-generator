from langgraph.graph import END, StateGraph

from resume_generator.agents.cover_letter_generator import CoverLetterGeneratorAgent
from resume_generator.agents.job_search import JobSearchAgent
from resume_generator.agents.profile_extractor import ProfileExtractorAgent
from resume_generator.agents.skills_matcher import SkillsMatcherAgent
from resume_generator.workflows.state import WorkflowState


def create_cover_letter_workflow():
    workflow = StateGraph(WorkflowState)

    # Initialize agents
    profile_agent = ProfileExtractorAgent()
    job_search_agent = JobSearchAgent()
    skills_agent = SkillsMatcherAgent()
    cover_letter_agent = CoverLetterGeneratorAgent()

    # Add nodes
    workflow.add_node("extract_profile", profile_agent.extract_profile)
    workflow.add_node("search_jobs", job_search_agent.search_jobs)
    workflow.add_node("match_skills", skills_agent.match_skills)
    workflow.add_node("generate_cover_letter", cover_letter_agent.generate_cover_letter)

    # Define the workflow flow
    workflow.set_entry_point("extract_profile")

    workflow.add_edge("extract_profile", "search_jobs")
    workflow.add_edge("search_jobs", "match_skills")
    workflow.add_edge("match_skills", "generate_cover_letter")
    workflow.add_edge("generate_cover_letter", END)

    return workflow.compile()


def should_continue(state: WorkflowState) -> str:
    if state.get("errors"):
        return END
    return "continue"
