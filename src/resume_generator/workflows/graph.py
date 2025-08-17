from langgraph.graph import StateGraph, END
from resume_generator.workflows.state import WorkflowState
from resume_generator.agents.profile_extractor import ProfileExtractorAgent
from resume_generator.agents.job_analyzer import JobAnalyzerAgent
from resume_generator.agents.skills_matcher import SkillsMatcherAgent
from resume_generator.agents.resume_generator import ResumeGeneratorAgent


def create_resume_workflow():
    workflow = StateGraph(WorkflowState)

    # Initialize agents
    profile_agent = ProfileExtractorAgent()
    job_agent = JobAnalyzerAgent()
    skills_agent = SkillsMatcherAgent()
    resume_agent = ResumeGeneratorAgent()

    # Add nodes
    workflow.add_node("extract_profile", profile_agent.extract_profile)
    workflow.add_node("analyze_job", job_agent.analyze_job)
    workflow.add_node("match_skills", skills_agent.match_skills)
    workflow.add_node("generate_resume", resume_agent.generate_resume)

    # Define the workflow flow
    workflow.set_entry_point("extract_profile")

    workflow.add_edge("extract_profile", "analyze_job")
    workflow.add_edge("analyze_job", "match_skills")
    workflow.add_edge("match_skills", "generate_resume")
    workflow.add_edge("generate_resume", END)

    return workflow.compile()


def should_continue(state: WorkflowState) -> str:
    if state.get("errors"):
        return END
    return "continue"
