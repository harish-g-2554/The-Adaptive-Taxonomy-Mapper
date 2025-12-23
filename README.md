# Adaptive Taxonomy Mapper

An AI-powered system that maps user-generated story tags to precise taxonomy categories using Groq's Llama 3.3 70B model.

---

## Overview

This project solves the problem of inconsistent user-generated tags by using AI to understand story context and map content to a predefined taxonomy. The system combines deterministic pattern matching with LLM-powered reasoning for accurate, explainable classifications.

**Key Features:**
- Context-aware classification - story content overrides misleading tags
- Returns `[UNMAPPED]` for content that doesn't fit the taxonomy
- Anti-hallucination validation ensures accuracy
- Comprehensive metrics and reporting
- 100% accuracy on test suite

---

## Installation

### Prerequisites
- Python 3.11+
- Groq API key ([Get free key](https://console.groq.com))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/adaptive-taxonomy-mapper.git
   cd adaptive-taxonomy-mapper
   ```

2. **Install dependencies**
   ```bash
   pip install groq python-dotenv
   ```

3. **Configure API key**
   
   Create `.env` file:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the mapper**
   ```bash
   python taxonomy_mapper.py
   ```

---

## Usage

### Basic Example

```python
from taxonomy_mapper import TaxonomyMapper

# Initialize
mapper = TaxonomyMapper()

# Classify a story
result = mapper.map_story(
    user_tags=["Love"],
    story_snippet="They hated each other for years...",
    case_id=1
)

print(result["mapped_category"])  # Output: Romance/Enemies-to-Lovers
print(result["confidence"])        # Output: 0.95
```

### Output

The system generates a detailed execution report:

```
======================================================================
  AI TAXONOMY MAPPER - EXECUTION REPORT
======================================================================

[OK] PROCESSING SUMMARY
   Total Cases: 10
   Successfully Mapped: 8
   Unmapped: 2
   Success Rate: 80.0%

[OK] AI METRICS
   Total LLM Calls: 8
   Total Tokens: 2006
   Estimated Cost: $0.0004
```

---

## How It Works

### Pipeline

1. **Pattern Matching** - Detect keywords to find candidate sub-genres
2. **LLM Inference** - Groq API analyzes story context
3. **Validation** - Verify output against known taxonomy
4. **Results** - Return category + confidence + reasoning

### Core Rules

- **Context Wins** - Story content > User tags
- **Honesty First** - Return `[UNMAPPED]` when uncertain
- **Validation** - All outputs checked against taxonomy

---

## Test Results

| Test Case | Input Tags | Result | Confidence |
|-----------|-----------|--------|------------|
| Case 1 | Love | Romance/Enemies-to-Lovers | 95% |
| Case 2 | Action, Spies | Thriller/Espionage | 95% |
| Case 3 | Scary, House | Horror/Gothic | 95% |
| Case 4 | Love, Future | Sci-Fi/Cyberpunk | 95% |
| Case 5 | Action | Thriller/Legal Thriller | 95% |
| Case 6 | Space | [UNMAPPED] | 99% |
| Case 7 | Sad, Love | Romance/Second Chance | 95% |
| Case 8 | Robots | Sci-Fi/Hard Sci-Fi | 95% |
| Case 9 | Ghost | Horror/Slasher | 95% |
| Case 10 | Recipe, Sweet | [UNMAPPED] | 99% |

**Success Rate: 100%** (10/10 correct)

---

## Project Structure

```
adaptive-taxonomy-mapper/
├── taxonomy_mapper.py       # Main classification engine
├── taxonomy.json            # Category definitions
├── test_cases.json          # Test suite
├── ai_reasoning_log.json    # Results (generated)
├── requirements.txt         # Dependencies
├── .env                     # API key (not in git)
└── README.md               # This file
```

---

## Configuration

### Custom Taxonomy

Edit `taxonomy.json`:

```json
{
  "Fiction": {
    "Romance": ["Slow-burn", "Enemies-to-Lovers"],
    "Thriller": ["Espionage", "Psychological"]
  }
}
```

### Environment Variables

`.env` file:
```
GROQ_API_KEY=your_key_here
```

---

## Performance

- **Model**: Llama 3.3 70B (Groq)
- **Speed**: 1-2 seconds per case
- **Cost**: ~$0.00004 per classification
- **Accuracy**: 100% on test suite
- **Rate Limits**: 30/min, 14,400/day (free tier)

---

## Technologies

- Python 3.11+
- Groq API (Llama 3.3 70B)
- python-dotenv

---

## Author

**Harish G**  
MSc Data Science

---

**Made with ❤️ using Groq AI**


