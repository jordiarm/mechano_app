from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()

practice_text_agent = Agent(
    name="Typing Practice Generator",
    instructions=(
        "You generate typing practice text for a speed-typing training app. "
        "The user will give you a list of weak keys (characters they frequently mistype) "
        "with error counts. Your job is to produce coherent, natural English sentences "
        "that heavily feature those characters.\n\n"
        "Rules:\n"
        "- Output ONLY the practice text, nothing else — no labels, no quotes, no explanation.\n"
        "- Write 40–60 words of flowing prose (multiple sentences).\n"
        "- Maximise usage of the weak characters while keeping the text readable.\n"
        "- Use common, easy-to-understand vocabulary.\n"
        "- Use only lowercase letters, spaces, and basic punctuation (periods, commas).\n"
        "- Do NOT use newlines, tabs, or special characters.\n"
        "- Vary sentence length for a natural typing rhythm."
    ),
    model="gpt-4o-mini",
)


async def generate_practice_text(weak_keys: list[dict]) -> str:
    """Generate AI practice text targeting the user's weak keys.

    Args:
        weak_keys: List of dicts with 'char' and 'count' keys,
                   e.g. [{"char": "j", "count": 12}, ...]

    Returns:
        A string of practice text.
    """
    prompt = "My weak keys (character: miss count):\n"
    for k in weak_keys:
        prompt += f"  {k['char']}: {k['count']} misses\n"
    prompt += "\nGenerate practice text that emphasises these characters."

    result = await Runner.run(practice_text_agent, input=prompt)
    return result.final_output
