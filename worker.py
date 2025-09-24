import argparse
import sys
from functools import partial
from typing import Optional
from dotenv import load_dotenv

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    WorkerType,
    cli,
)
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import (
    deepgram,
    silero,
    noise_cancellation,
    bey
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from agent.lesson_agent_plugin import LessonAgentPlugin


async def entrypoint(ctx: JobContext, avatar_id: Optional[str]) -> None:
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    session = AgentSession(
        stt=deepgram.STT(),
        llm=LessonAgentPlugin(),
        tts=deepgram.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    if avatar_id is not None:
        bey_avatar_session = bey.AvatarSession(avatar_id=avatar_id)
    else:
        bey_avatar_session = bey.AvatarSession()

    await bey_avatar_session.start(session, room=ctx.room)

    await session.start(
        room=ctx.room,
        agent=Agent(instructions=""),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(instructions="Start the lesson!")


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run a LiveKit agent with Bey avatar.")
    parser.add_argument("--avatar-id", default="694c83e2-8895-4a98-bd16-56332ca3f449", type=str, help="Avatar ID to use.")
    args = parser.parse_args()

    sys.argv = [sys.argv[0], "start"]

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=partial(entrypoint, avatar_id=args.avatar_id),
            worker_type=WorkerType.ROOM,
            port=6002
        )
    )
