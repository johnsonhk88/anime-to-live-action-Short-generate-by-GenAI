def plan_cinematic_shot(scene_description: str, style_notes: str, reference_images: list[str]) -> dict:
    """Plan a cinematic shot based on scene description and style guidance.

    Args:
        scene_description: Text description of the scene to shoot.
        style_notes: Artistic style guidance.
        reference_images: Paths to reference images for visual consistency.

    Returns:
        Dict with shot plan including camera, lighting, and composition details.
    """
    return {
        "camera": {
            "angle": "low_angle",
            "movement": "dolly_zoom",
            "lens": "50mm prime",
            "aperture": "f/1.8",
            "focal_length": 50,
        },
        "lighting": {
            "setup": "three_point",
            "key_light": "warm_orange_from_top_right",
            "fill_light": "cool_blue_from_bottom_left",
            "back_light": "rim_light_from_behind",
            "mood": "dramatic_contrast",
        },
        "composition": {
            "framing": "rule_of_thirds",
            "subject_position": "right_third",
            "depth": "shallow_depth_of_field_with_foreground_elements",
            "color_grading": "teal_and_orange_with_crushed_blacks",
        },
        "duration_seconds": 4.5,
        "description": scene_description,
        "reference_images": reference_images,
    }


def calculate_camera_movement(shot_a: dict, shot_b: dict) -> dict:
    """Calculate the camera movement needed to transition between two shots.

    Args:
        shot_a: The first shot's camera configuration.
        shot_b: The second shot's camera configuration.

    Returns:
        Dict with transition type and movement parameters.
    """
    return {
        "transition_type": "whip_pan",
        "direction": "left_to_right",
        "speed": "fast",
        "duration_seconds": 0.3,
        "continuity_notes": "Maintains spatial awareness - hero moves from right to left across frame",
    }
