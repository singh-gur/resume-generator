import json
from pathlib import Path

import click

from resume_generator.workflows.graph import create_resume_workflow
from resume_generator.workflows.state import WorkflowState


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AI-powered resume generator using LangChain and LangGraph.

    Generate personalized resumes by analyzing user profiles and searching for
    available job opportunities through multiple specialized agents.
    """
    pass


@cli.command()
@click.option(
    "--profile",
    "-p",
    required=True,
    type=click.Path(exists=True),
    help="Path to user profile file (text or JSON)",
)
@click.option(
    "--location",
    "-l",
    default="Remote",
    help="Job search location (default: Remote)",
)
@click.option(
    "--job-sites",
    multiple=True,
    default=["indeed", "linkedin", "glassdoor"],
    type=click.Choice(["indeed", "linkedin", "glassdoor"]),
    help="Job sites to search (can specify multiple)",
)
@click.option(
    "--max-results",
    default=20,
    type=int,
    help="Maximum number of jobs to search (default: 20)",
)
@click.option(
    "--hours-old",
    default=72,
    type=int,
    help="Only include jobs posted within this many hours (default: 72)",
)
@click.option(
    "--output",
    "-o",
    default="generated_resume.json",
    help="Output file path for generated resume",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text", "markdown"]),
    default="json",
    help="Output format",
)
def generate(
    profile: str,
    location: str,
    job_sites: tuple,
    max_results: int,
    hours_old: int,
    output: str,
    output_format: str,
):
    """Generate personalized resumes based on user profile and available job opportunities."""

    try:
        # Read profile file
        profile_text = Path(profile).read_text(encoding="utf-8")

        click.echo("🚀 Starting resume generation workflow...")
        click.echo(f"🔍 Searching for jobs in: {location}")
        click.echo(f"📊 Max results: {max_results}, Sites: {', '.join(job_sites)}")

        # Initialize workflow
        workflow = create_resume_workflow()

        # Prepare initial state with job search parameters
        initial_state: WorkflowState = {
            "user_profile_raw": profile_text,
            "job_description_raw": None,  # Will be populated by job search
            "user_profile": None,
            "job_description": None,
            "job_matches": None,
            "skill_matches": None,
            "generated_resume": None,
            "errors": [],
            "step_completed": [],
            # Add job search parameters to state for JobSearchAgent
            "job_search_location": location,
            "job_sites": list(job_sites),
            "max_results": max_results,
            "hours_old": hours_old,
        }

        # Run workflow
        click.echo("📝 Extracting user profile...")
        result = workflow.invoke(initial_state)

        # Check for errors
        if result.get("errors"):
            click.echo("❌ Errors occurred during processing:")
            for error in result["errors"]:
                click.echo(f"  • {error}")
            raise click.Abort()

        # Get generated resume
        generated_resume = result.get("generated_resume")
        if not generated_resume:
            click.echo("❌ Failed to generate resume")
            raise click.Abort()

        # Save output
        output_path = Path(output)

        if output_format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(generated_resume.model_dump(), f, indent=2, default=str)
        elif output_format == "text":
            formatted_resume = format_resume_as_text(generated_resume)
            output_path.write_text(formatted_resume, encoding="utf-8")
        elif output_format == "markdown":
            formatted_resume = format_resume_as_markdown(generated_resume)
            output_path.write_text(formatted_resume, encoding="utf-8")

        click.echo("✅ Resume generated successfully!")
        click.echo(f"📄 Output saved to: {output_path}")
        click.echo(f"🎯 Match percentage: {generated_resume.match_percentage:.1f}%")

        # Show tailoring notes
        if generated_resume.tailoring_notes:
            click.echo("\n💡 Tailoring suggestions:")
            for note in generated_resume.tailoring_notes:
                click.echo(f"  • {note}")

    except FileNotFoundError as e:
        click.echo(f"❌ Profile file not found: {e}")
        raise click.Abort() from e
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON in profile file: {e}")
        raise click.Abort() from e
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        raise click.Abort() from e


@cli.command()
@click.option(
    "--output",
    "-o",
    default=".ignore/example_profile.txt",
    help="Output file path for example profile",
)
def create_profile_template(output: str):
    """Create an example user profile template."""

    template = """John Doe
Software Engineer

Contact Information:
Email: john.doe@email.com
Phone: (555) 123-4567
LinkedIn: https://linkedin.com/in/johndoe
GitHub: https://github.com/johndoe
Location: San Francisco, CA

Professional Summary:
Experienced software engineer with 5+ years of experience in full-stack development. 
Proficient in Python, JavaScript, and cloud technologies. Strong background in building 
scalable web applications and working in agile environments.

Technical Skills:
- Programming Languages: Python, JavaScript, TypeScript, Java
- Frameworks: React, Node.js, Django, Flask
- Databases: PostgreSQL, MongoDB, Redis
- Cloud: AWS, Docker, Kubernetes
- Tools: Git, Jenkins, JIRA

Work Experience:

Senior Software Engineer | TechCorp Inc.
January 2022 - Present
- Led development of microservices architecture serving 1M+ users daily
- Implemented CI/CD pipelines reducing deployment time by 50%
- Mentored junior developers and conducted code reviews
- Technologies: Python, Django, AWS, Docker, PostgreSQL

Software Engineer | StartupXYZ
June 2020 - December 2021
- Developed React-based frontend applications
- Built RESTful APIs using Node.js and Express
- Collaborated with design team to implement responsive UI components
- Technologies: React, Node.js, MongoDB, JavaScript

Education:
Bachelor of Science in Computer Science
University of California, Berkeley
Graduated: May 2020
GPA: 3.7/4.0
Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering

Projects:
E-commerce Platform
- Built full-stack e-commerce application with React and Django
- Implemented payment processing with Stripe integration
- Deployed on AWS with auto-scaling capabilities
- Technologies: React, Django, PostgreSQL, AWS, Docker

Task Management App
- Developed real-time task management application
- Implemented WebSocket connections for live updates
- Used Redux for state management
- Technologies: React, Node.js, Socket.io, MongoDB

Certifications:
AWS Certified Solutions Architect - Associate | Amazon Web Services | 2023
Certified Kubernetes Administrator (CKA) | Cloud Native Computing Foundation | 2022

Languages:
English (Native), Spanish (Conversational)
"""

    Path(output).write_text(template, encoding="utf-8")
    click.echo(f"✅ Profile template created: {output}")
    click.echo("Edit this file with your information and use it with the --profile option.")


def format_resume_as_text(resume) -> str:
    """Format the generated resume as plain text."""
    sections = []

    # Header
    sections.append(f"{resume.user_profile.full_name}")
    sections.append("=" * len(resume.user_profile.full_name))
    sections.append("")

    # Professional Summary
    sections.append("PROFESSIONAL SUMMARY")
    sections.append("-" * 20)
    sections.append(resume.customized_summary)
    sections.append("")

    # Resume sections
    for section in sorted(resume.sections, key=lambda x: x.priority):
        sections.append(section.section_name.upper())
        sections.append("-" * len(section.section_name))
        sections.append(section.content)
        sections.append("")

    # Match info
    sections.append(f"JOB MATCH: {resume.match_percentage:.1f}%")

    return "\n".join(sections)


def format_resume_as_markdown(resume) -> str:
    """Format the generated resume as Markdown."""
    sections = []

    # Header
    sections.append(f"# {resume.user_profile.full_name}")
    sections.append("")

    # Professional Summary
    sections.append("## Professional Summary")
    sections.append(resume.customized_summary)
    sections.append("")

    # Resume sections
    for section in sorted(resume.sections, key=lambda x: x.priority):
        sections.append(f"## {section.section_name}")
        sections.append(section.content)
        sections.append("")

    # Match info
    sections.append(f"**Job Match:** {resume.match_percentage:.1f}%")

    return "\n".join(sections)


if __name__ == "__main__":
    cli()
