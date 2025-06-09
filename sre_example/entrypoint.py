import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Intelligent SRE",
        description="An agent system for SRE",
        epilog="Welcome use Intelligent SRE @ Bytedance ARK Team",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=["workflow", "llm"],
        default="workflow",
        help="Choose the mode to run the system. Default is workflow mode.",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="The prompt to run the system. Can be a natural language or an alert from monitor.",
    )
    parser.add_argument(
        "-s",
        "--enable-sampling",
        action="store_true",
        help="Enable sampling for the system. Default is False.",
    )

    args = parser.parse_args()

    if args.mode == "workflow":
        from sre_example.workflow_mode import main

        main(prompt=args.prompt, enable_sampling=args.enable_sampling)
    elif args.mode == "llm":
        from sre_example.llm_mode import main

        main(prompt=args.prompt, enable_sampling=args.enable_sampling)
