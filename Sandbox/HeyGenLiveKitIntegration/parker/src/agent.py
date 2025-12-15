import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
)
from livekit.plugins import liveavatar, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Default instructions used when no skill is specified
DEFAULT_INSTRUCTIONS = """You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
You eagerly assist users with their questions by providing information from your extensive knowledge.
Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
You are curious, friendly, and have a sense of humor."""

# Path to skills directory (relative to this file)
SKILLS_DIR = Path(__file__).parent / "skills"


def load_skill(skill_name: str) -> str:
    """Load skill instructions from a markdown file.

    Args:
        skill_name: Name of the skill (e.g., "skill1", "skill2", "skill3")

    Returns:
        The content of the skill markdown file, or DEFAULT_INSTRUCTIONS if not found.
    """
    skill_path = SKILLS_DIR / f"{skill_name}.md"

    if skill_path.exists():
        logger.info(f"Loading skill from {skill_path}")
        return skill_path.read_text()
    else:
        logger.warning(
            f"Skill file not found: {skill_path}, using default instructions"
        )
        return DEFAULT_INSTRUCTIONS


class Assistant(Agent):
    def __init__(self, instructions: str = DEFAULT_INSTRUCTIONS) -> None:
        super().__init__(
            instructions=instructions,
        )

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="parker")
async def my_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Parse room metadata to determine which skill to load
    # Expected format: {"skill": "skill1"} or {"skill": "skill2"} etc.
    instructions = DEFAULT_INSTRUCTIONS
    if ctx.job.metadata:
        try:
            metadata = json.loads(ctx.job.metadata)
            skill_name = metadata.get("skill")
            if skill_name:
                instructions = load_skill(skill_name)
                logger.info(f"Using skill: {skill_name}")
            else:
                logger.info(
                    "No skill specified in metadata, using default instructions"
                )
        except json.JSONDecodeError as e:
            logger.warning(
                f"Failed to parse job metadata as JSON: {e}, using default instructions"
            )
    else:
        logger.info("No job metadata provided, using default instructions")

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=inference.STT(model="assemblyai/universal-streaming", language="en"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=inference.TTS(
            model="cartesia/sonic-3", voice="b134c304-d095-4d2b-a77a-914f5e8e84e7"
        ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Add HeyGen LiveAvatar to the session
    # Requires LIVEAVATAR_API_KEY and LIVEAVATAR_AVATAR_ID in .env.local
    # For more info, see https://docs.livekit.io/agents/models/avatar/plugins/liveavatar
    avatar = liveavatar.AvatarSession()
    # Start the avatar and wait for it to join the room
    await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(instructions=instructions),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony()
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                else noise_cancellation.BVC(),
            ),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

    # Greet the user with a welcome message
    await session.say(
        "Hello! My name's Parker, I'm a communications coach who will be teaching you today. Ready to dive into it?"
    )


if __name__ == "__main__":
    cli.run_app(server)
