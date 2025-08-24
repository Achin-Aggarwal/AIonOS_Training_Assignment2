# card_builder.py
from botbuilder.schema import Attachment
import json

def build_software_card(app_name: str, versions: list[str]) -> Attachment:
    """
    Returns an adaptive card attachment for a given app with version choices.
    """
    card_json = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock", 
                "text": f"📦 Install {app_name.title()}", 
                "weight": "Bolder", 
                "size": "Large",
                "color": "Accent"
            },
            {
                "type": "TextBlock", 
                "text": "Please select the version you want to install:", 
                "size": "Medium",
                "spacing": "Medium"
            },
            {
                "type": "Input.ChoiceSet",
                "id": "version",
                "style": "compact",
                "placeholder": "Choose version...",
                "choices": [{"title": f"Version {v}", "value": v} for v in versions]
            }
        ],
        "actions": [
            {
                "type": "Action.Submit", 
                "title": "🚀 Proceed With Installation", 
                "data": {
                    "action": "install",
                    "app": app_name,
                    "timestamp": "{{DATE()}}"
                }
            }
        ]
    }

    return Attachment(content_type="application/vnd.microsoft.card.adaptive", content=card_json)


def build_software_selection_card(catalog: dict) -> Attachment:
    """
    Returns an adaptive card for software selection when user wants to install software 
    but didn't specify which ones.
    """
    # Create choices from catalog
    choices = []
    for app_name, versions in catalog.items():
        latest_version = versions[-1] if versions else "Unknown"
        choices.append({
            "title": f"{app_name.title()} (Latest: {latest_version})",
            "value": app_name
        })
    
    # Sort choices alphabetically
    choices.sort(key=lambda x: x["title"])
    
    card_json = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock", 
                "text": "🛠️ Software Installation Center", 
                "weight": "Bolder", 
                "size": "Large",
                "color": "Accent"
            },
            {
                "type": "TextBlock", 
                "text": "Select the software you want to install from our catalog:", 
                "size": "Medium",
                "spacing": "Medium",
                "wrap": True
            },
            {
                "type": "Input.ChoiceSet",
                "id": "selected_software",
                "style": "expanded",
                "isMultiSelect": True,
                "choices": choices,
                "placeholder": "Select one or more software..."
            }
        ],
        "actions": [
            {
                "type": "Action.Submit", 
                "title": "📋 Show Installation Options", 
                "data": {
                    "action": "show_versions",
                    "timestamp": "{{DATE()}}"
                }
            }
        ]
    }

    return Attachment(content_type="application/vnd.microsoft.card.adaptive", content=card_json)


