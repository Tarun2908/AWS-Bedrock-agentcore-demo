"""
Deploy agent.py to Amazon Bedrock AgentCore Runtime using the starter toolkit.

Three phases: configure -> launch -> invoke. Observability is turned on by the
toolkit (it sets AGENT_OBSERVABILITY_ENABLED=true for you). We only add the
content-extraction opt-out so prompt/response text is kept in the spans, which
Omni's Trace Explorer and the evaluators read.

Run:  python deploy.py
Prereq: `uv pip install bedrock-agentcore-starter-toolkit`  (or pip)
"""

from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session

REGION = Session().region_name or "us-east-1"
AGENT_NAME = "omni_demo_agent"

runtime = Runtime()

# ---- Phase 1: Configure -----------------------------------------------------
# Auto-creates the execution role and an ECR repo, and generates a Dockerfile
# from agent.py. disable_otel is left at its default (False) so AgentCore
# Observability / Omni telemetry stays ON.
runtime.configure(
    entrypoint="agent.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=REGION,
    agent_name=AGENT_NAME,
)

# ---- Phase 2: Launch --------------------------------------------------------
# AGENT_OBSERVABILITY_ENABLED is injected by the runtime automatically — do NOT
# pass it yourself. The only env var we add is the content opt-out so span text
# is retained for tracing + evaluation.
launch_result = runtime.launch(
    env_vars={
        "AWS_GENAI_CONTENT_EXTRACTION_OPT_OUT": "true",
    }
)
print("Deployed. Agent ARN:", launch_result["agent_arn"])

# ---- Phase 3: Invoke (generates your first trace) ---------------------------
resp = runtime.invoke({"prompt": "What's the weather in Mumbai?"})
print("Response:", resp)
resp = runtime.invoke({"prompt": "Give me a one-line summary of what an AI agent is."})
print("Response:", resp)
print("\nOpen CloudWatch Omni to see these two runs as traces.")
