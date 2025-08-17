from typing import Any, Dict, List

from jobspy import scrape_jobs

from resume_generator.agents.base import BaseAgent
from resume_generator.models.schemas import JobListing, JobMatches, UserProfile


class JobSearchAgent(BaseAgent):
    def search_jobs(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_profile: UserProfile = state.get("user_profile")
            if not user_profile:
                return {
                    **state,
                    "errors": state.get("errors", [])
                    + ["User profile not found for job search"],
                }

            # Extract search parameters from state or use defaults from user profile
            location = (
                state.get("job_search_location")
                or user_profile.contact_info.location
                or "Remote"
            )
            job_sites = state.get("job_sites") or ["indeed", "linkedin", "glassdoor"]
            max_results = state.get("max_results") or 20
            hours_old = state.get("hours_old") or 72

            # Generate search keywords from skills and experience
            search_keywords = self._generate_search_keywords(user_profile)

            # Determine if searching for remote jobs
            is_remote_search = location.lower() in ["remote", "anywhere", "global"]

            # Search for jobs using jobspy
            jobs_df = scrape_jobs(
                site_name=job_sites,
                search_term=" ".join(search_keywords[:3]),  # Limit to top 3 keywords
                location=location if not is_remote_search else "Remote",
                results_wanted=max_results,
                hours_old=hours_old,
                country_indeed="USA",
            )

            # Convert DataFrame to JobListing objects
            job_listings = []
            if jobs_df is not None and not jobs_df.empty:
                for _, row in jobs_df.iterrows():
                    job_listing = JobListing(
                        title=str(row.get("title", "")),
                        company=str(row.get("company", "")),
                        location=str(row.get("location", "")),
                        description=str(row.get("description", ""))[
                            :500
                        ],  # Truncate description
                        job_url=str(row.get("job_url", "")),
                        date_posted=str(row.get("date_posted", "")),
                        job_type=str(row.get("job_type", "")),
                        salary=str(row.get("salary", "")),
                        is_remote=self._is_remote_job(row),
                    )
                    job_listings.append(job_listing)

            # Create JobMatches object
            job_matches = JobMatches(
                search_location=location,
                search_keywords=search_keywords,
                is_remote_search=is_remote_search,
                jobs=job_listings,
                total_results=len(job_listings),
            )

            return {
                **state,
                "job_matches": job_matches,
                "step_completed": state.get("step_completed", []) + ["job_search"],
            }

        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Job search failed: {str(e)}"],
            }

    def _generate_search_keywords(self, user_profile: UserProfile) -> List[str]:
        keywords = []

        # Add top skills
        keywords.extend(user_profile.skills[:5])

        # Add recent job titles from experience
        if user_profile.experience:
            recent_positions = [exp.position for exp in user_profile.experience[:2]]
            keywords.extend(recent_positions)

        # Add technologies from recent experience
        for exp in user_profile.experience[:2]:
            keywords.extend(exp.technologies_used[:3])

        # Remove duplicates and empty strings
        keywords = list(set([k.strip() for k in keywords if k.strip()]))

        return keywords[:10]  # Limit to top 10 keywords

    def _is_remote_job(self, job_row) -> bool:
        location = str(job_row.get("location", "")).lower()
        description = str(job_row.get("description", "")).lower()

        remote_indicators = ["remote", "work from home", "wfh", "anywhere", "virtual"]

        return any(
            indicator in location or indicator in description
            for indicator in remote_indicators
        )

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return self.search_jobs(state)
