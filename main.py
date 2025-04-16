from dotenv import load_dotenv
import logging
from pathlib import Path
from typing import AsyncIterable, Optional, Dict, Any, Type

from pathlib import Path
import wave
import asyncio
from livekit import rtc
from livekit.agents import (
    JobContext, WorkerOptions, cli, APIConnectOptions, function_tool, RunContext,
    AudioConfig, BackgroundAudioPlayer, BuiltinAudioClip
)
from livekit.agents.voice import Agent, AgentSession
from dataclasses import dataclass, field
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    silero
)

# Setup logging
logger = logging.getLogger("dual-agent")
logger.setLevel(logging.INFO)

# Set up data to share between agents
@dataclass
class UserData:
    """Stores data to be shared across the session"""
    current_agent: str = "general"
    general_agent: Optional[Agent] = None
    product_agent: Optional[Agent] = None
    last_query: str = ""
    
    def summarize(self) -> str:
        return f"Current agent: {self.current_agent}, Last query: {self.last_query}"

load_dotenv()


def load_product_info():
    """Load the product information from the product-info.md file."""
    try:
        with open("product-info.md", "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error loading product information: {e}")
        return "Product information not available."


# System prompt for the general-purpose assistant
GENERAL_ASSISTANT_PROMPT = """
You are Alex, a helpful and friendly AI assistant. Your primary goal is to assist users with any general questions they might have.

Your responsibilities include:
1. Answering general knowledge questions on a wide range of topics
2. Providing helpful information about various subjects
3. Being conversational and engaging with users
4. Being honest when you don't know the answer to a question

When asked about specific product information, explain that you'll hand over to Ana, the product specialist who has detailed information about the company's catalog.

Always be friendly, professional, and concise in your voice responses.
"""

# System prompt for the product specialist assistant
PRODUCT_ASSISTANT_PROMPT = """
You are Ana, a knowledgeable product specialist for our product catalog.

You have access to the following product information:

{productinfo}

Your responsibilities include:
1. Accurately describing products and their features based on the provided information
2. Comparing different products when asked about differences
3. Providing detailed pricing information when requested
4. Making personalized product recommendations based on customer needs
5. Answering questions about product specifications, availability, and compatibility
6. Being honest when you don't know the answer to a question outside of your product knowledge

Always be friendly, professional, and concise in your voice responses. Avoid making up information not contained in the product catalog. If you're uncertain about any details, acknowledge the limitations of your knowledge and offer to help with what you do know.
"""


# Product-related keywords
PRODUCT_KEYWORDS = [
    "product", "price", "cost", "purchase", "buy", "model", "device",
    "scanner", "computer", "barcode", "mobile", "handheld", "order",
    "catalog", "inventory", "specifications", "specs", "features",
    "compare", "difference", "scanner", "ruggedized", "rugged", "warranty",
    "carema", "zebra", "honeywell", "datalogic", "point mobile", "urovo",
    "bluebird", "m3 mobile", "newland", "unitech"
]

class GeneralAssistant(Agent):
    """General-purpose assistant for answering non-product related questions."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=GENERAL_ASSISTANT_PROMPT,
            stt=deepgram.STT(model="nova-3", language="multi"),
            llm=openai.LLM(
                model="gpt-4.1-mini-2025-04-14",
                temperature=0.4
            ),
            tts=openai.TTS(model="gpt-4o-mini-tts", voice="alloy"),
            vad=silero.VAD.load()
        )
    
    async def on_enter(self):
        """Initial greeting when the agent joins."""
        logger.info("General assistant started, providing initial greeting")
        await self.session.generate_reply(
            instructions="Greet the user warmly and introduce yourself as Alex, a general assistant who can answer various questions. Mention that for specific product inquiries, you can connect them with Ana, the product specialist."
        )
    
    @function_tool()
    async def switch_to_product_assistant(self, context: RunContext[UserData], query: str) -> Agent:
        """
        Switch to the product specialist when a product-related query is detected.
        
        Args:
            query: The user's query that triggered the switch
        """
        logger.info(f"Switching to product assistant for: {query}")
        
        # Store the query in userdata for context
        context.userdata.last_query = query
        
        # Play transition sound when switching to product specialist
        if background_audio:
            background_audio.play("transition.wav")
        
        # Tell the user we're switching
        await self.session.say("I'll connect you with Ana, our product specialist who can help with your product questions.")
        
        # Get the product agent from userdata and pass chat context
        product_agent = context.userdata.product_agent
        
        # Set current agent in userdata
        context.userdata.current_agent = "product"
        
        # Return the product agent to trigger handoff
        return product_agent
    
    # Remove local method since we'll play sound directly during handoff


class ProductAssistant(Agent):
    """Product specialist assistant for answering product-related questions."""
    
    def __init__(self) -> None:
        # Load product information
        product_info = load_product_info()
        
        # Format the system prompt with product information
        instructions = PRODUCT_ASSISTANT_PROMPT.format(productinfo=product_info)
        
        # Initialize the agent with the enhanced prompt and extended timeout
        super().__init__(
            instructions=instructions,
            stt=deepgram.STT(model="nova-3", language="multi"),
            llm=openai.LLM(
                model="gpt-4.1-mini-2025-04-14",
                temperature=0.4,
                 
            ),
            tts=openai.TTS(model="gpt-4o-mini-tts", voice="nova"),
            vad=silero.VAD.load()
        )
        
    # Function to simulate product research without sound
    @function_tool()
    async def research_product_info(self, context: RunContext[UserData], query: str) -> Dict[str, Any]:
        """
        Take time to look up detailed product information.
        Use this when you need to provide detailed product specifications or comparisons.
        
        Args:
            query: The specific product information being researched
        """
        logger.info(f"Ana is researching product information: {query}")
        
        # Simulate research time without sound
        await asyncio.sleep(1)
        
        return {
            "status": "complete",
            "message": "I've found the detailed information you requested."
        }
    
    async def on_enter(self):
        """Initial greeting when the agent joins."""
        logger.info("Product assistant started, providing initial greeting")
        # Get the last query if available
        last_query = self.session.userdata.last_query
        if last_query:
            await self.session.generate_reply(
                instructions=f"Introduce yourself as Ana, the product specialist, and address this product question: '{last_query}'"
            )
        else:
            await self.session.generate_reply(
                instructions="Introduce yourself as Ana, the product specialist, and ask how you can help with product questions."
            )
    
    @function_tool()
    async def switch_to_general_assistant(self, context: RunContext[UserData], query: str) -> Agent:
        """
        Switch to the general assistant when a non-product query is detected.
        
        Args:
            query: The user's query that triggered the switch
        """
        logger.info(f"Switching to general assistant for: {query}")
        
        # Store the query in userdata for context
        context.userdata.last_query = query
        
        # Play transition sound when switching to general assistant
        if background_audio:
            background_audio.play("transition.wav")
        
        # Tell the user we're switching
        await self.session.say("I'll connect you back with Alex, our general assistant who can help with your questions.")
        
        # Get the general agent from userdata
        general_agent = context.userdata.general_agent
        
        # Set current agent in userdata
        context.userdata.current_agent = "general"
        
        # Return the general agent to trigger handoff
        return general_agent
        
    # Remove local method since we'll play sound directly during handoff
            
    # No need for thinking sound method


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    logger.info("Starting dual-agent system...")
    
    # Configure API connection options for better handling of timeouts
    api_options = APIConnectOptions(
        max_retry=5,          # Increase retries from default 3
        retry_interval=1.0,   # Longer interval between retries (default 2.0)
        timeout=60.0          # Longer timeout for API calls (default 10.0)
    )
    
    # Create both agents
    general_agent = GeneralAssistant()
    product_agent = ProductAssistant()
    
    # Initialize user data with agent references
    userdata = UserData(
        current_agent="general",
        general_agent=general_agent,
        product_agent=product_agent
    )
    
    # Create session with userdata
    session = AgentSession[UserData](userdata=userdata)
    
    # Function to check if a query is product related
    def is_product_query(query: str) -> bool:
        query = query.lower()
        return any(keyword in query for keyword in PRODUCT_KEYWORDS)
    
    # Create a global reference to store the BackgroundAudioPlayer that can be accessed by all code
    global background_audio
    background_audio = None  # Initialize to None
    
    # Setup background audio player only for transition sounds
    bg_player = BackgroundAudioPlayer(
        # No ambient sound in the background
        ambient_sound=None,
        # No thinking sounds needed
        thinking_sound=None
    )
    
    # Store the player in our global variable for use by the agents
    background_audio = bg_player
    
    # No llm_thinking handler needed
    
    # We'll handle sound directly in the play_transition_sound methods
    
    # Start with the general assistant
    await session.start(
        agent=general_agent,
        room=ctx.room
    )
    
    # Start background audio player
    await background_audio.start(room=ctx.room, agent_session=session)
    
    # Set up transcript handler to check for agent switching with context transfer
    # We need to use a synchronous callback with session.on()
    @session.on("transcript")
    def on_transcript(transcript):
        # Use asyncio.create_task to run the async processing
        import asyncio
        asyncio.create_task(process_transcript(transcript))
    
    # Track the last user query for context passing
    last_query = ""
    
    # Separate async function to process transcripts
    async def process_transcript(transcript):
        nonlocal last_query
        try:
            query = transcript.text
            if not query or len(query.strip()) == 0:
                return
            
            # Store query for context transfer
            last_query = query
            
            logger.info(f"Received transcript: {query}")
            current_agent = session.userdata.current_agent
            
            # Check if we should switch agents based on content
            should_use_product = is_product_query(query)
            
            if should_use_product and current_agent == "general":
                logger.info("Auto-switching to product assistant based on content")
                
                # Create chat context with history for memory transfer
                chat_ctx = product_agent.chat_ctx.copy()
                
                # Copy the last message from general agent to product agent
                chat_ctx.add_message(
                    role="user",
                    content=f"The user asked about: {query}"
                )
                
                # Play transition sound - directly call play before switching
                background_audio.play("transition.wav")
                
                # Set state and update agent
                session.userdata.current_agent = "product"
                await session.update_agent(product_agent)
                
                # Update chat context
                await product_agent.update_chat_ctx(chat_ctx)
                
                # Make Ana introduce herself and address the query
                await session.generate_reply(
                    instructions=f"Introduce yourself as Ana, the product specialist, and address this product question: '{query}'"
                )
                
            elif not should_use_product and current_agent == "product":
                logger.info("Auto-switching to general assistant based on content")
                
                # Create chat context with history for memory transfer
                chat_ctx = general_agent.chat_ctx.copy()
                
                # Copy the last message from product agent to general agent
                chat_ctx.add_message(
                    role="user",
                    content=f"The user asked about: {query}"
                )
                
                # Play transition sound - directly call play before switching
                background_audio.play("transition.wav")
                
                # Set state and update agent
                session.userdata.current_agent = "general"
                await session.update_agent(general_agent)
                
                # Update chat context
                await general_agent.update_chat_ctx(chat_ctx)
                
                # Make Alex introduce himself
                await session.generate_reply(
                    instructions=f"Introduce yourself as Alex, the general assistant, and address this question: '{query}'"
                )
            
        except Exception as e:
            logger.error(f"Error processing transcript: {e}")
    
    # Log function calls for debugging
    @session.on("function_call")
    def on_function_call(event):
        logger.info(f"Function call detected: {event.name} with args: {event.arguments}")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))