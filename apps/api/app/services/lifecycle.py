def automation_hooks() -> list[str]:
    return ["customer.created", "ticket.escalated", "conversation.resolved", "subscription.renewal_risk"]
