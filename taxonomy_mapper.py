import json
import os
import time
import logging
from typing import List, Tuple
from groq import Groq
from dotenv import load_dotenv

# ------------------------------------------------------
# Logging Configuration (Errors only by design)
# ------------------------------------------------------
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class TaxonomyMapper:
    """
    Adaptive Taxonomy Mapper
    ------------------------
    Deterministic-first classification system with LLM-assisted disambiguation,
    hallucination protection, and execution metrics.
    """

    def __init__(self, taxonomy_path: str = "taxonomy.json"):
        # Load taxonomy
        with open(taxonomy_path, "r") as f:
            self.taxonomy = json.load(f)

        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

        # Build validation set
        self.valid_categories = self._build_valid_category_set()

        # Metrics
        self.llm_call_count = 0
        self.total_tokens = 0
        self.validation_triggers = 0
        self.hallucinations_caught = 0

        # Deterministic semantic keyword map
        self.keyword_map = {
            "Enemies-to-Lovers": ["enemy", "enemies", "rival", "hate", "tension"],
            "Slow-burn": ["slow", "gradual", "years", "patience"],
            "Second Chance": ["again", "reunite", "years later", "return", "ex-"],
            "Espionage": ["spy", "agent", "intelligence", "covert", "cia", "mi6"],
            "Psychological": ["mind", "obsession", "paranoia", "sanity"],
            "Legal Thriller": ["lawyer", "court", "trial", "judge", "verdict"],
            "Hard Sci-Fi": ["physics", "quantum", "engineering", "stasis"],
            "Space Opera": ["galaxy", "empire", "fleet", "interstellar"],
            "Cyberpunk": ["cyber", "neon", "hacker", "dystopia", "ai"],
            "Psychological Horror": ["terror", "madness", "fear", "nightmare"],
            "Gothic": ["mansion", "haunted", "fog", "castle", "shadows"],
            "Slasher": ["killer", "murder", "blood", "stalks", "masked"]
        }

    # ------------------------------------------------------
    # Taxonomy Utilities
    # ------------------------------------------------------

    def _build_valid_category_set(self) -> set:
        valid = set()
        for _, genres in self.taxonomy.items():
            for genre, subgenres in genres.items():
                if not isinstance(subgenres, list):
                    raise ValueError("Invalid taxonomy format: expected list of subgenres")
                for subgenre in subgenres:
                    valid.add(f"{genre}/{subgenre}")
        return valid

    # ------------------------------------------------------
    # Deterministic Candidate Extraction
    # ------------------------------------------------------

    def _extract_candidate_subgenres(self, story_snippet: str) -> Tuple[List[str], List[str]]:
        snippet = story_snippet.lower()
        candidates = set()
        matched_patterns = []

        for _, genres in self.taxonomy.items():
            for genre, subgenres in genres.items():
                for subgenre in subgenres:
                    keywords = self.keyword_map.get(subgenre, [])
                    hits = [kw for kw in keywords if kw in snippet]
                    if hits:
                        candidates.add(f"{genre}/{subgenre}")
                        matched_patterns.extend(hits)

        return list(candidates), matched_patterns

    # ------------------------------------------------------
    # Prompt Construction
    # ------------------------------------------------------

    def _build_prompt(self, candidates: List[str], user_tags, story_snippet: str) -> str:
        return f"""
You are assisting a taxonomy classification system.

ALLOWED SUB-GENRES (STRICT):
{candidates}

RULES:
1. Choose ONLY from the list above.
2. If none apply, respond with "[UNMAPPED]".
3. Story context overrides user tags.
4. Do NOT invent category names.

User Tags: {user_tags}
Story Snippet: "{story_snippet}"

Respond ONLY in valid JSON:
{{
  "mapped_category": "Genre/Sub-genre or [UNMAPPED]",
  "confidence": 0.95,
  "reasoning": "Brief justification based on story context"
}}
"""

    # ------------------------------------------------------
    # Validation Layer (Anti-Hallucination)
    # ------------------------------------------------------

    def _validate_mapping(self, mapped_category: str) -> Tuple[str, bool]:
        if mapped_category == "[UNMAPPED]":
            return mapped_category, False

        if mapped_category in self.valid_categories:
            return mapped_category, False

        self.hallucinations_caught += 1
        return "[UNMAPPED]", True

    # ------------------------------------------------------
    # Core Classification Pipeline
    # ------------------------------------------------------

    def map_story(self, user_tags, story_snippet, case_id):
        candidates, patterns = self._extract_candidate_subgenres(story_snippet)

        if not candidates:
            return {
                "mapped_category": "[UNMAPPED]",
                "confidence": 0.99,
                "reasoning": "No deterministic semantic signals matched taxonomy.",
                "validated": False,
                "patterns": []
            }

        prompt = self._build_prompt(candidates, user_tags, story_snippet)

        self.llm_call_count += 1
        self.total_tokens += len(prompt.split())

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )

        content = response.choices[0].message.content.strip()
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()

        llm_output = json.loads(content)

        final_category, validated = self._validate_mapping(llm_output["mapped_category"])
        if validated:
            self.validation_triggers += 1

        return {
            "mapped_category": final_category,
            "confidence": llm_output.get("confidence", 0.85),
            "reasoning": llm_output["reasoning"],
            "validated": validated,
            "patterns": patterns[:5]
        }

    # ------------------------------------------------------
    # Batch Processing
    # ------------------------------------------------------

    def process_test_cases(self, test_cases_path="test_cases.json"):
        with open(test_cases_path, "r") as f:
            test_cases = json.load(f)

        results = []

        for case in test_cases:
            try:
                result = self.map_story(
                    case["user_tags"],
                    case["story_snippet"],
                    case["id"]
                )
                time.sleep(0.5)
            except Exception as e:
                result = {
                    "mapped_category": "[UNMAPPED]",
                    "confidence": 0.0,
                    "reasoning": f"System error: {str(e)}",
                    "validated": False,
                    "patterns": []
                }

            results.append({
                "test_case_id": case["id"],
                "mapped_category": result["mapped_category"],
                "confidence": result["confidence"],
                "validated": result["validated"],
                "reasoning": result["reasoning"],
                "expected_logic": case.get("expected_logic", "")
            })

        return results

    # ------------------------------------------------------
    # Reporting
    # ------------------------------------------------------

    def save_results(self, results, output_path="reasoning_log.json"):
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

    def print_execution_report(self, results):
        mapped = [r for r in results if r["mapped_category"] != "[UNMAPPED]"]
        unmapped = [r for r in results if r["mapped_category"] == "[UNMAPPED]"]

        total_cases = len(results)
        success_rate = (len(mapped) / total_cases * 100) if total_cases else 0
        avg_tokens = (self.total_tokens / self.llm_call_count) if self.llm_call_count else 0
        estimated_cost = (self.total_tokens / 1_000_000) * 0.20  # approx Groq pricing

        print("\n" + "=" * 70)
        print("AI TAXONOMY MAPPER - EXECUTION REPORT")
        print("=" * 70)
        print()
        print("[OK] PROCESSING SUMMARY")
        print(f"   Total Cases: {total_cases}")
        print(f"   Successfully Mapped: {len(mapped)}")
        print(f"   Unmapped: {len(unmapped)}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        print("[OK] AI METRICS")
        print(f"   Total LLM Calls: {self.llm_call_count}")
        print(f"   Total Tokens: {self.total_tokens}")
        print(f"   Avg Tokens/Case: {avg_tokens:.1f}")
        print(f"   Estimated Cost: ${estimated_cost:.4f}")
        print()
        print("[OK] VALIDATION & SAFETY")
        print(f"   Validation Triggers: {self.validation_triggers}")
        print(f"   Hallucinations Caught: {self.hallucinations_caught}")
        print()
        print("[OK] DETAILED RESULTS")
        print("-" * 70)
        print()

        for r in results:
            print(f"[>] Case {r['test_case_id']}: {r.get('user_tags', [])}")
            print(f"   Classification: {r['mapped_category']}")
            print(f"   Confidence: {r.get('confidence', 0.0)}")
            print(f"   Validated: {'Yes' if r.get('validated') else 'No'}")

            reasoning = r.get("reasoning", "")
            reasoning_short = reasoning[:150] + "..." if len(reasoning) > 150 else reasoning
            print(f"   Reasoning: {reasoning_short}")
            print()

        print("=" * 70)
        print("[OK] Analysis Complete! Check 'reasoning_log.json' for full details.")
        print("=" * 70)



# ------------------------------------------------------
# Entry Point
# ------------------------------------------------------

def main():
    mapper = TaxonomyMapper()
    results = mapper.process_test_cases()
    mapper.save_results(results)
    mapper.print_execution_report(results)


if __name__ == "__main__":
    main()
