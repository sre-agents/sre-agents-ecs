from deepeval.test_case import ToolCall

data = [
    {
        "prompt": {
            "instance": "i-0123456789abcdef0",
            "region": "us-west-2",
            "command_content": "ls -l",
        },
        "expected_tools": [
            ToolCall(
                name="mock_ecs_server_tool",
                arguments={
                    "instance": "i-0123456789abcdef0",
                    "region": "us-west-2",
                    "command_content": "ls -l",
                },
            )
        ],
    },
    {
        "prompt": {
            "instance": "i-abcdef01234567890",
            "region": "ap-northeast-1",
            "command_content": "pwd",
        },
        "expected_tools": [
            ToolCall(
                name="mock_ecs_server_tool",
                arguments={
                    "instance": "i-abcdef01234567890",
                    "region": "ap-northeast-1",
                    "command_content": "pwd",
                },
            )
        ],
    },
    {
        "prompt": {
            "instance": "i-9876543210fedcba",
            "region": "eu-central-1",
            "command_content": "whoami",
        },
        "expected_tools": [
            ToolCall(
                name="mock_ecs_server_tool",
                arguments={
                    "instance": "i-9876543210fedcba",
                    "region": "eu-central-1",
                    "command_content": "whoami",
                },
            )
        ],
    },
    {
        "prompt": {
            "instance": "i-0abc123def456ghi",
            "region": "sa-east-1",
            "command_content": "df -h",
        },
        "expected_tools": [
            ToolCall(
                name="mock_ecs_server_tool",
                arguments={
                    "instance": "i-0abc123def456ghi",
                    "region": "sa-east-1",
                    "command_content": "df -h",
                },
            )
        ],
    },
]
