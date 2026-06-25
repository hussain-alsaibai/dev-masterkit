# prompt-engineering — Skill for Writing Effective System Prompts

## Trigger

Use when the user asks to:
- "Write a system prompt for..."
- "Create instructions for my AI assistant"
- "How do I prompt an LLM to..."
- "Make my prompts more effective"
- "Prompt template for [task]"

## Description

Designs system prompts and instruction templates that produce consistent,
predictable, high-quality output from AI assistants. Focuses on clarity,
constraint specification, and output format control.

## Procedure

### 1. Identify the Goal

Determine what the prompt needs to accomplish:
- **Task execution:** "Do X and return Y"
- **Persona adoption:** "Act as a senior engineer..."
- **Format control:** "Return JSON with these fields..."
- **Quality gating:** "Only include verified information..."

### 2. Structure the Prompt

Use this template:

```
## Role
[Who the AI is - persona, expertise level, style]

## Task
[What to do - specific, measurable, actionable]

## Constraints
[What NOT to do - boundaries, exclusions, limits]

## Output Format
[How to structure the response - markdown, JSON, tables]

## Examples
[Show 1-2 examples of ideal output]

## Rules
[Numbered list of non-negotiable rules]
```

### 3. Write Clear Instructions

| Bad | Good |
|-----|------|
| "Make it good" | "Include error handling for all edge cases" |
| "Be detailed" | "Provide a code example for each API method" |
| "Fix the code" | "Replace `eval()` with `ast.literal_eval()` and add input validation" |
| "Check everything" | "Verify: 1) All tests pass, 2) No secrets in code, 3) Type hints present" |

### 4. Add Format Control

Explicitly specify output format:

```
Return your response in this format:

## Summary
[1-2 sentence overview]

## Details
[Bullet points or numbered steps]

## Code
[Only if relevant - fenced code blocks with language tag]

## Next Steps
[Actionable items, who does what]
```

### 5. Include Constraints

Define boundaries to prevent unwanted behavior:

```
Constraints:
- Do not use third-party libraries (stdlib only)
- Do not modify existing API signatures
- Do not include placeholder text like "TODO" or "FIXME"
- Do not return explanations without code when code is requested
```

### 6. Provide Examples

One example beats a paragraph of description:

```
Example input: "Create a URL validator"
Example output:
```python
def validate_url(url: str) -> bool:
    """Return True if URL is valid HTTP/HTTPS."""
    return url.startswith(("http://", "https://"))
```
```

### 7. Test and Iterate

After writing:
1. Read the prompt as if you're the AI — is anything ambiguous?
2. Run a test generation — does output match expectations?
3. Add missing constraints based on deviations
4. Remove redundant instructions

## Validation Checklist

- [ ] Role is clearly defined (who the AI is being)
- [ ] Task is specific and actionable
- [ ] Constraints prevent common failure modes
- [ ] Output format is explicitly specified
- [ ] At least one example is provided
- [ ] Rules are numbered and non-negotiable
- [ ] Prompt is under 500 tokens (shorter = better adherence)
- [ ] Tested with at least one sample input

## Notes

- Shorter prompts with clear structure beat longer, rambling prompts
- Order matters: role → task → constraints → format → examples
- Negative constraints ("don't X") are as important as positive ones ("do Y")
- Update prompts based on actual output quality, not theoretical perfection

## Last Verified: 2026-06-25
