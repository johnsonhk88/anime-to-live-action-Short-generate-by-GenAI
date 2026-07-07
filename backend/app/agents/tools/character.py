def design_character_sheet(character_data: dict, style_notes: str = "") -> dict:
    """Design a detailed live-action character sheet from anime character analysis.

    Args:
        character_data: Character analysis data including appearance and features.
        style_notes: Art style observations to inform the live-action design.

    Returns:
        Dict with live-action character descriptions for casting and generation.
    """
    return {
        "name": character_data.get("name", "Unknown"),
        "live_action_appearance": {
            "face": "Strong jawline, sharp cheekbones, defined brow",
            "hair": character_data.get("appearance", "").split(",")[0] if character_data.get("appearance") else "Dark hair, medium length",
            "eyes": "Intense, slightly narrowed, with a hint of otherworldly glow",
            "build": "Athletic, tall, commanding presence",
            "skin_tone": "Fair with warm undertones",
        },
        "wardrobe": {
            "primary_outfit": "Modern reinterpretation of anime costume using high-end textured fabrics",
            "colors": character_data.get("color_palette", ["#1a1a2e", "#e94560"]),
            "accessories": [feature for feature in character_data.get("key_features", [])],
        },
        "casting_notes": "Needs actor with strong screen presence and ability to convey intensity through subtle expressions",
        "reference_prompts": [
            f" cinematic portrait of {character_data.get('name', 'a character')}, live-action, photorealistic, dramatic lighting, shallow depth of field, 4K",
            f" {character_data.get('name', 'a character')} in action pose, movie still, cinematic lighting, realistic texture, high detail",
        ],
    }


def generate_expression_set(character_sheet: dict) -> dict:
    """Generate a set of expression references for a designed character.

    Args:
        character_sheet: The output from design_character_sheet.

    Returns:
        Dict with expression descriptions and generation prompts.
    """
    return {
        "character": character_sheet["name"],
        "expressions": [
            {"type": "neutral", "prompt": f" portrait of {character_sheet['name']}, neutral expression, looking at camera, live-action, cinematic lighting, photorealistic"},
            {"type": "happy", "prompt": f" portrait of {character_sheet['name']}, warm genuine smile, joyful expression, live-action, soft lighting, photorealistic"},
            {"type": "angry", "prompt": f" portrait of {character_sheet['name']}, intense angry stare, furrowed brow, dramatic shadows, live-action, cinematic"},
            {"type": "determined", "prompt": f" portrait of {character_sheet['name']}, determined expression, focused eyes, heroic pose, live-action, epic lighting"},
        ],
    }
