from __future__ import annotations

import sys

from research_crew.crew import ResearchCrew


def run():
  topic = (
    " ".join(sys.argv[1:])
    if len(sys.argv) > 1
    else "The current state and future of AI agents in 2025"
  )
  print(f"Researching: {topic}\n")
  result = ResearchCrew().crew().kickoff(inputs={"topic": topic})
  print("\n=== Research Complete ===")
  print(result.raw)


if __name__ == "__main__":
  run()
