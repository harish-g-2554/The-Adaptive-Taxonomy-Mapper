# Taxonomy Mapping – System Design Document

## 1. How would you handle a taxonomy with 5,000 categories instead of 12?

With 5,000 categories, sending the entire taxonomy to the LLM in every prompt would be slow, expensive, and unreliable.

Instead, I would:

- Organize the taxonomy hierarchically (Genre → Sub-genre → Fine-grained category)
- Use embeddings, keyword matching, or lightweight classifiers to narrow the taxonomy to a small candidate set (for example, the top 20–30 relevant categories)
- Send only these shortlisted categories to the LLM for final reasoning and selection

This approach keeps prompts small, improves accuracy, and allows the system to scale cleanly as the taxonomy grows.

---

## 2. How would you minimize LLM costs if you process 1 million stories per month?

I would design the system so the LLM is **not called for every story**.

My approach would include:

- Using cheap pre-filters first (rules, keyword matching, embeddings, or classical classifiers)
- Sending only ambiguous or high-value stories to the LLM
- Batching requests where possible
- Using smaller, cheaper models for classification instead of large general-purpose models
- Caching results for repeated or very similar inputs

In practice, the LLM becomes a **decision-maker of last resort**, not the default step, which significantly reduces overall cost.

---

## 3. How do you ensure the model doesn’t hallucinate sub-genres not present in the JSON?

I treat the taxonomy JSON as the **single source of truth**.

To prevent hallucinations:

- I explicitly list valid categories in the prompt
- I enforce structured JSON output
- I validate the model’s response after generation

If the returned category does not exist in the taxonomy, the system automatically:

- Rejects it
- Corrects it if possible
- Or falls back to `[UNMAPPED]`

This ensures that even if the model makes a mistake, the system never accepts invalid output.
