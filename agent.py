"""
Sample agentic AI for Amazon Bedrock AgentCore + CloudWatch Omni observability.

A minimal Strands agent with one tool. AgentCore Runtime wraps it via the
BedrockAgentCoreApp entrypoint. Strands emits OpenTelemetry spans natively;
the AWS Distro for OpenTelemetry (installed via requirements.txt) exports them,
and AgentCore Runtime turns export on when AGENT_OBSERVABILITY_ENABLED=true
(the starter toolkit sets this for you).

Nothing in this file talks to CloudWatch directly — telemetry flows out through
the runtime. That is the whole point: instrument once, observe everywhere.
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()


# ---- A simple tool so Omni's Trace Explorer has a tool span to show ----
@tool
def get_weather(city: str) -> str:
    """Return a canned weather string for a city (demo tool)."""
    table = {
        "seattle": "cloudy, 14C",
        "mumbai": "humid, 31C",
        "london": "rainy, 11C",
    }
    return f"The weather in {city} is {table.get(city.lower(), 'sunny, 22C')}."


# Nova Lite is cheap and fast — good for a demo. Swap for any Bedrock model id.
model = BedrockModel(model_id="amazon.nova-lite-v1:0")

agent = Agent(
    model=model,
    tools=[get_weather],
    system_prompt=(
        "You are a concise assistant. When asked about weather, "
        "call the get_weather tool. Otherwise answer directly."
    ),
)


@app.entrypoint
def invoke(payload):
    """AgentCore Runtime calls this per request. `payload` is the JSON body."""
    prompt = payload.get("prompt", "Hello!")
    result = agent(prompt)
    return {"result": result.message}


if __name__ == "__main__":
    # Lets you run locally too:  python agent.py   then POST to :8080/invocations
    app.run()
