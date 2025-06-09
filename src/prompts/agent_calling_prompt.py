SUB_AGENT_INFO_TEMPLATE = """Sub agent No.{id}
Name: {name}
Description: {description}
Expected input format: {input_schema}
Expected output format: {output_schema}
"""

AGENT_CALLING_PROMPT = """You can call the following sub-agents via `call_agent` function to help you:
"""
