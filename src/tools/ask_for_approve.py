def ask_for_approve(command: str, risk_level: str, reason: str):
    """Asks for approval based on the given command and risk level.

    Args:
        command (str): The command for which approval is being sought.
        risk_level (str): The risk level associated with the command. Must be one of "high", "medium", "low".
        reason (str): The reason for the risk level.

    Returns:
        dict: A dictionary containing the command and approval status. The approval status is True if the command is approved, and False otherwise.

    Raises:
        AssertionError: If the risk level is not one of "high", "medium", "low".
    """
    assert risk_level in ["high", "medium", "low"]
    print("****** Command execution approve request ******")
    if risk_level == "low":
        print(
            f"Command: {command}\nRisk level: {risk_level}\nReason: {reason}\nApproved automatically."
        )
        return {"command": command, "approved": True}
    elif risk_level == "medium" or risk_level == "high":
        approve = input(
            f"Command: {command}\nRisk level: {risk_level}\nReason: {reason}\nApprove? (y/n)"
        )
        if approve == "y":
            return {"command": command, "approved": True}
        else:
            return {"command": command, "approved": False}
