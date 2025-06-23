import random
import asyncio
import nest_asyncio
from src.agent import Agent
from src.memory.short_term_memory import ShortTermMemory

nest_asyncio.apply()


# --- Define a Simple Tool Function (Same as before) ---
def get_city_weather(city: str) -> dict[str, str]:
    """Retrieves the weather information of a given city."""
    print(f"--- Tool 'get_city_weather' executing with city: {city} ---")
    weather_conditions = [
        "Sunny",
        "Cloudy",
        "Rainy",
        "Partly cloudy",
        "Windy",
        "Snowy",
        "Humid",
        "Hazy",
        "Cool",
        "Hot",
    ]
    # Generate a random integer between 0 and 9,
    # where 0 represents a 10% chance of not finding the information.
    if random.randint(0, 9) == 0:
        return {"result": f"Weather information not found for {city}"}
    else:
        condition = random.choice(weather_conditions)
        temperature = random.randint(-10, 40)
        return {"result": f"{condition}, {temperature}°C"}


async def run():
    apmplus_agent = Agent(
        name="weather",
        description="An LLM agent demonstrating callback",
        system_prompt="You are a weather query Agent who can call tools to query the weather and output the results",
        tools=[get_city_weather],
        enable_tracing=True,
        short_term_memory=await ShortTermMemory.create(),
    )

    response = await apmplus_agent.run(prompt="what's the weather in beijing")
    print(response)


if __name__ == "__main__":
    asyncio.run(run())
