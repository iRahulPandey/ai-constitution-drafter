# Citation Gap Locator (CGL)

A tool for identifying and exploiting Citation Gaps in Generative Engine Optimization (GEO) to improve AI citation rates and search visibility.

## What is a Citation Gap?

A **Citation Gap** is a concept specific to Generative Engine Optimization (GEO). It refers to the specific missing elements—structure, data, or directness—that prevent current top-ranking content from being the "primary source" an AI chooses to quote.

### GEO vs Traditional SEO

- **Traditional SEO**: A "Content Gap" means your competitors have keywords you don't
- **GEO**: A Citation Gap means your competitors have the information, but they are presenting it in a way that is hard for an AI to parse, summarize, or trust

## The Three Types of Citation Gaps

### 1. The Structural Gap *(Most Common)*

**Problem**: LLMs (Large Language Models) are lazy. They prefer content that is pre-formatted for extraction. If a competitor answers a question in a long, dense paragraph, there is a Structural Gap.

**Example Scenario**: 
- **User Query**: "Compare PyTorch vs TensorFlow for production"
- **Competitor Approach**: Writes a 2,000-word essay with buried details
- **The Gap**: Lack of a clear, side-by-side comparison
- **Solution**: Provide a markdown comparison table with rows for "Latency," "Deployment," and "Ecosystem"

> 💡 **Why it works**: The AI will almost always cite the table over the essay because it requires less processing power to summarize.

### 2. The Semantic Gap *(The "Direct Answer" Problem)*

**Problem**: When an AI generates a "Featured Snippet" or direct chat response, it looks for a concise definition that's immediately accessible.

**Example Scenario**:
- **User Query**: "What is a reverse proxy?"
- **Competitor Approach**: Starts with a story: "In the early days of the internet, servers were..." and eventually defines it in the third paragraph
- **The Gap**: The answer is not "retrievable" in the first 200 tokens
- **Solution**: Place a Definition Block at the very top: "A reverse proxy is a server that sits in front of web servers and forwards client requests to those web servers."

> 💡 **Why it works**: The AI grabs this sentence verbatim and cites you.

### 3. The Data Recency Gap

**Problem**: LLMs are trained on massive datasets with a cutoff date, but they prioritize "grounding" (searching the live web) for current facts.

**Example Scenario**:
- **User Query**: "Best AI agents 2026"
- **Competitor Approach**: Has an article titled "Best AI Agents" but the pricing and features are from 2024
- **The Gap**: The data is "stale" (low confidence)
- **Solution**: Find current pricing and explicitly label it "Updated Jan 2026"

> 💡 **Why it works**: The AI's grounding mechanism will prioritize your freshness signal over the competitor's domain authority.

## How Citation Gaps Work

```
┌─────────────────┐    ┌─────────────────┐
│   Competitor    │    │       You       │
│                 │    │                 │
│ High Cognitive  │ vs │ Low Cognitive   │
│ Load (Hard to   │    │ Load (Easy to   │
│ Summarize)      │    │ Summarize)      │
└─────────────────┘    └─────────────────┘
        │                        │
        └────────────────────────┼─────► AI Cites You
```

The AI looks at the "Competitor" and sees high cognitive load (hard to summarize). It looks at "You" and sees low cognitive load (easy to summarize). **It cites You.**

## Agent Architecture

This project uses a three-agent system to identify and exploit citation gaps:

| Agent | Task | Citation Gap Logic |
|-------|------|-------------------|
| **Researcher** | Fetch | Gets the top 3 Google results for target queries |
| **Judge** | Evaluate | Checks: "Do these results have tables? Do they have direct answers? Are they recent?" If NO, returns `status='pass'` (gap found) |
| **Builder** | Synthesize | Writes content specifically designed to fill identified gaps (e.g., generating comparison tables when competitors lack structured data) |

## Key Benefits

- **Higher AI Citation Rates**: Content optimized for AI parsing and extraction
- **Reduced Cognitive Load**: Structured, easily digestible information formats
- **Competitive Advantage**: Exploit gaps in competitor content presentation
- **Future-Proof SEO**: Optimize for AI-driven search experiences

---

*Updated January 2026 - Optimized for current AI search patterns*