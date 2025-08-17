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
    """Generate a resume from a profile with job search context."""

    try:
        profile_path = Path(profile)
        profile_content = profile_path.read_text(encoding="utf-8")

        # Simpler detection: use file extension
        is_json_profile = profile_path.suffix.lower() == ".json"
        click.echo("📋 Detected JSON profile format" if is_json_profile else "📋 Detected text profile format")

        click.echo("🚀 Starting resume generation workflow...")
        click.echo(f"🔍 Searching for jobs in: {location}")
        click.echo(f"📊 Max results: {max_results}, Sites: {', '.join(job_sites)}")

        workflow = create_resume_workflow()

        initial_state: WorkflowState = {
            "user_profile_raw": None if is_json_profile else profile_content,
            "user_profile_json": profile_content if is_json_profile else None,
            "job_description_raw": None,
            "user_profile": None,
            "job_description": None,
            "job_matches": None,
            "skill_matches": None,
            "generated_resume": None,
            "errors": [],
            "step_completed": [],
            "job_search_location": location,
            "job_sites": list(job_sites),
            "max_results": max_results,
            "hours_old": hours_old,
        }

        result = workflow.invoke(initial_state)

        errors = result.get("errors") or []
        if errors:
            click.echo("❌ Errors occurred during processing:")
            for error in errors:
                click.echo(f"  • {error}")
            raise click.Abort()

        generated_resume = result.get("generated_resume")
        if not generated_resume:
            click.echo("❌ Failed to generate resume")
            raise click.Abort()

        output_path = Path(output)
        output_path.write_text(render_resume(generated_resume, output_format), encoding="utf-8")

        click.echo("✅ Resume generated successfully!")
        click.echo(f"📄 Output saved to: {output_path}")
        click.echo(f"🎯 Match percentage: {generated_resume.match_percentage:.1f}%")

        notes = getattr(generated_resume, "tailoring_notes", None) or []
        if notes:
            click.echo("\n💡 Tailoring suggestions:")
            for note in notes:
                click.echo(f"  • {note}")

    except FileNotFoundError as e:
        click.echo(f"❌ Profile file not found: {e}")
        raise click.Abort() from e
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        raise click.Abort() from e


@cli.command()
@click.option(
    "--output",
    "-o",
    default="profile_template.json",
    help="Output file path for example profile",
)
@click.option(
    "--format",
    "template_format",
    type=click.Choice(["json", "text"]),
    default="json",
    help="Template format (default: json)",
)
def create_profile_template(output: str, template_format: str):
    """Create an example user profile template."""

    if template_format == "json":
        template = {
            "full_name": "John Doe",
            "contact_info": {
                "email": "john.doe@email.com",
                "phone": "(555) 123-4567",
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe",
                "portfolio": "https://johndoe.dev",
                "location": "San Francisco, CA",
            },
            "professional_summary": (
                "Experienced software engineer with 5+ years of experience in full-stack development. "
                "Proficient in Python, JavaScript, and cloud technologies. Strong background in building "
                "scalable web applications and working in agile environments."
            ),
            "skills": [
                "Python",
                "JavaScript",
                "TypeScript",
                "Java",
                "React",
                "Node.js",
                "Django",
                "Flask",
                "PostgreSQL",
                "MongoDB",
                "Redis",
                "AWS",
                "Docker",
                "Kubernetes",
                "Git",
                "Jenkins",
                "JIRA",
            ],
            "education": [
                {
                    "institution": "University of California, Berkeley",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "graduation_date": "2020-05-01",
                    "gpa": 3.7,
                    "relevant_coursework": ["Data Structures", "Algorithms", "Database Systems", "Software Engineering"],
                }
            ],
            "experience": [
                {
                    "company": "TechCorp Inc.",
                    "position": "Senior Software Engineer",
                    "start_date": "2022-01-01",
                    "end_date": None,
                    "description": (
                        "Lead development of microservices architecture serving 1M+ users daily. "
                        "Implement CI/CD pipelines and mentor junior developers."
                    ),
                    "key_achievements": [
                        "Led development of microservices architecture serving 1M+ users daily",
                        "Implemented CI/CD pipelines reducing deployment time by 50%",
                        "Mentored junior developers and conducted code reviews",
                    ],
                    "technologies_used": ["Python", "Django", "AWS", "Docker", "PostgreSQL"],
                },
                {
                    "company": "StartupXYZ",
                    "position": "Software Engineer",
                    "start_date": "2020-06-01",
                    "end_date": "2021-12-01",
                    "description": "Developed React-based frontend applications and built RESTful APIs using Node.js.",
                    "key_achievements": [
                        "Developed React-based frontend applications",
                        "Built RESTful APIs using Node.js and Express",
                        "Collaborated with design team to implement responsive UI components",
                    ],
                    "technologies_used": ["React", "Node.js", "MongoDB", "JavaScript"],
                },
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Built full-stack e-commerce application with React and Django",
                    "technologies_used": ["React", "Django", "PostgreSQL", "AWS", "Docker"],
                    "url": "https://github.com/johndoe/ecommerce-platform",
                    "achievements": [
                        "Implemented payment processing with Stripe integration",
                        "Deployed on AWS with auto-scaling capabilities",
                    ],
                },
                {
                    "name": "Task Management App",
                    "description": "Developed real-time task management application",
                    "technologies_used": ["React", "Node.js", "Socket.io", "MongoDB"],
                    "url": "https://github.com/johndoe/task-manager",
                    "achievements": ["Implemented WebSocket connections for live updates", "Used Redux for state management"],
                },
            ],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect - Associate",
                    "issuer": "Amazon Web Services",
                    "issue_date": "2023-01-01",
                    "expiry_date": "2026-01-01",
                    "credential_url": "https://aws.amazon.com/certification/verify",
                },
                {
                    "name": "Certified Kubernetes Administrator (CKA)",
                    "issuer": "Cloud Native Computing Foundation",
                    "issue_date": "2022-01-01",
                    "expiry_date": "2025-01-01",
                    "credential_url": None,
                },
            ],
            "languages": ["English (Native)", "Spanish (Conversational)"],
        }

        with open(output, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, default=str)

    else:  # text format
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


def render_resume(resume, fmt: str) -> str:
    """Render resume content into the requested format as a string."""
    if fmt == "json":
        return json.dumps(resume.model_dump(), indent=2, default=str)
    if fmt == "text":
        return format_resume_as_text(resume)
    return format_resume_as_markdown(resume)


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
