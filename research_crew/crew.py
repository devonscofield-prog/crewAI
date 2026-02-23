from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from research_crew.tools.search_tools import scrape_webpage, search_web


@CrewBase
class ResearchCrew:
  """Research & Intelligence Crew — conducts multi-source research,
  cross-validates findings, and produces a well-sourced analytical report."""

  agents_config = "config/agents.yaml"
  tasks_config = "config/tasks.yaml"

  # ── Agents ──────────────────────────────────────────────────────────

  @agent
  def research_planner(self) -> Agent:
    return Agent(
      config=self.agents_config["research_planner"],
      verbose=True,
    )

  @agent
  def web_researcher(self) -> Agent:
    return Agent(
      config=self.agents_config["web_researcher"],
      tools=[search_web, scrape_webpage],
      verbose=True,
    )

  @agent
  def data_analyst(self) -> Agent:
    return Agent(
      config=self.agents_config["data_analyst"],
      allow_code_execution=True,
      verbose=True,
    )

  @agent
  def fact_checker(self) -> Agent:
    return Agent(
      config=self.agents_config["fact_checker"],
      verbose=True,
    )

  @agent
  def report_writer(self) -> Agent:
    return Agent(
      config=self.agents_config["report_writer"],
      verbose=True,
    )

  # ── Tasks ───────────────────────────────────────────────────────────

  @task
  def planning_task(self) -> Task:
    return Task(config=self.tasks_config["planning_task"])

  @task
  def web_research_task(self) -> Task:
    return Task(config=self.tasks_config["web_research_task"])

  @task
  def data_analysis_task(self) -> Task:
    return Task(config=self.tasks_config["data_analysis_task"])

  @task
  def fact_checking_task(self) -> Task:
    return Task(
      config=self.tasks_config["fact_checking_task"],
      guardrail=self._validate_sourced_claims,
      guardrail_max_retries=2,
    )

  @task
  def report_writing_task(self) -> Task:
    return Task(
      config=self.tasks_config["report_writing_task"],
      output_file="research_report.md",
    )

  # ── Guardrails ──────────────────────────────────────────────────────

  @staticmethod
  def _validate_sourced_claims(task_output) -> tuple[bool, str]:
    """Every claim in the fact-check report must reference at least one source."""
    text = task_output.raw.lower()
    has_sources = any(
      marker in text
      for marker in ["http", "source:", "according to", "[", "citation"]
    )
    if has_sources:
      return True, task_output.raw
    return False, "Each claim must reference at least one source. Please add source citations."

  # ── Crew ────────────────────────────────────────────────────────────

  @crew
  def crew(self) -> Crew:
    return Crew(
      agents=self.agents,
      tasks=self.tasks,
      process=Process.sequential,
      verbose=True,
      memory=True,
    )
