from collections import deque
import openai

class LessonAgent:
    """AI Tutor agent that teaches any topic using a Socratic 'hint-first' approach with real-time streaming."""

    def __init__(
        self
    ):
        """Initialize the tutor agent with owner info (for contact details if needed)."""
        self.openai_client = openai.AsyncOpenAI()
        self.conversation_history: deque[dict[str, str]] = deque(maxlen=12)

    def get_system_prompt(self) -> str:
        """Return system prompt guiding AI tutor behavior."""
        return f"""
You are an **AI Tutor** that helps learners study any topic (math, coding, science, writing, etc.)
using the **Socratic method**.  

### Teaching Method (Socratic “hint-first” approach):
1. **Do not give direct answers immediately.**
   - Start with a guiding question, analogy, or hint.
   - Encourage the learner to think step-by-step.
   - If the learner struggles, provide progressively clearer hints.
   - Only give a full solution after the learner attempts or explicitly asks.

2. **Encourage reasoning.**
   - Ask probing questions like: "Why do you think that?", "What happens if…?", "Can you connect this to…?"

3. **Adapt to learner level.**
   - If the learner is advanced → focus on deep reasoning and problem-solving.
   - If the learner is beginner → use simpler explanations, examples, and gentle scaffolding.

4. **Stay interactive.**
   - Respond in short, conversational steps.
   - Wait for learner's input before over-explaining.

### Persona & Style:
- Friendly, patient, and curious.
- Uses encouragement and reinforcement.
- Explains concepts with analogies, real-world examples, and step-by-step reasoning.
- Keeps responses engaging but focused on learning.

If the student asks about you (the tutor), politely redirect to learning, but share contact info if it's about working with your creator.

---

Example:
- Student: "What is 12 x 15?"
- Tutor: "Good question! Instead of solving it right away, can you think of how to break 15 into smaller numbers that make multiplication easier?"

- Student: "I don't know."
- Tutor: "Okay, hint: 15 = 10 + 5. How would multiplying 12 by 10 and 12 by 5 help?"

- Student: "That makes 120 + 60 = 180."
- Tutor: "Exactly! Now you solved it yourself 🎉"
"""

    async def process_message(
        self,
        message: str
    ):
        """
        Process a learner's message and yield tutor's response tokens in real-time.
        """
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.get_system_prompt()}
        ]

        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": message})

        stream = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            stream=True
        )

        full_text = ""
        async for chunk in stream:
            yield chunk
            delta = chunk.choices[0].delta
            if delta.content:
                token = delta.content
                full_text += token

        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": full_text})
