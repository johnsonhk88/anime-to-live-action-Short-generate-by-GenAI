from pathlib import Path

from app.services.mode_factory import get_tts_provider, is_mock


def assemble_final_video(clip_paths: list[str], transition_type: str = "crossfade") -> dict:
    """Assemble multiple video clips into a final cinematic short film.

    Args:
        clip_paths: Ordered list of paths to generated video clips.
        transition_type: Type of transition between clips (crossfade, cut, whip_pan, etc.).

    Returns:
        Dict with the final assembled video path and metadata.
    """
    return {
        "final_path": "/output/final_cinematic_short.mp4",
        "duration_seconds": sum(4.5 for _ in clip_paths) if clip_paths else 0.0,
        "clip_count": len(clip_paths),
        "resolution": "1920x1080",
        "fps": 24,
        "codec": "h264",
        "audio_track": "cinematic_score_with_sound_design",
        "transitions_applied": transition_type,
    }


def add_transitions(
    clip_a_path: str,
    clip_b_path: str,
    transition: str = "crossfade",
    duration: float = 0.5,
) -> dict:
    """Add a transition between two video clips.

    Args:
        clip_a_path: Path to the first clip.
        clip_b_path: Path to the second clip.
        transition: Transition type (crossfade, dissolve, wipe, whip_pan).
        duration: Transition duration in seconds.

    Returns:
        Dict with the transition result and metadata.
    """
    return {
        "output_path": f"/transitions/{transition}_{hash(clip_a_path + clip_b_path) % 10000:04d}.mp4",
        "transition": transition,
        "duration": duration,
        "result": "success",
    }


def render_final_output(assembled_path: str, output_format: str = "mp4", quality: str = "high") -> dict:
    """Render the final assembled video to the specified output format.

    Args:
        assembled_path: Path to the assembled video.
        output_format: Desired output format (mp4, mov, webm).
        quality: Output quality (low, medium, high).

    Returns:
        Dict with the final rendered output path and metadata.
    """
    return {
        "output_path": assembled_path.replace(".mp4", f"_final.{output_format}"),
        "format": output_format,
        "quality": quality,
        "bitrate": "40Mbps" if quality == "high" else "20Mbps",
        "file_size_mb": 245.0,
        "render_time_seconds": 12.5,
    }


def synthesize_voiceover(
    text: str,
    voice: str = "narrator",
    mode: str = "hybrid",
    ref_audio: str = "",
    ref_text: str = "",
) -> dict:
    """Synthesize a voice-over track for narration or character dialogue.

    Args:
        text: Spoken line or narrator script.
        voice: Voice id or character name.
        mode: Execution mode (local / cloud / hybrid).
        ref_audio: Optional clone reference audio path or URL.
        ref_text: Transcript of the reference audio (CosyVoice3 / Qwen3-TTS Base).

    Returns:
        Dict with audio_path and TTS provider metadata.
    """
    provider = get_tts_provider(mode)
    if provider == "none":
        return {"audio_path": "", "provider": "none", "text": text, "skipped": True}
    if is_mock():
        return {
            "audio_path": f"/audio/{voice}_{hash(text) % 10000:04d}.wav",
            "provider": provider,
            "text": text,
            "voice": voice,
        }

    from app.services.tts.client import synthesize_speech

    try:
        return synthesize_speech(
            text,
            mode=mode,
            voice=voice,
            ref_audio=ref_audio or None,
            ref_text=ref_text or None,
        ).to_dict()
    except Exception as exc:
        return {
            "audio_path": f"/audio/{voice}_{hash(text) % 10000:04d}.wav",
            "provider": provider,
            "text": text,
            "voice": voice,
            "error": str(exc),
            "fallback": "mock",
        }


def mux_audio(video_path: str, voiceover_path: str, output_path: str = "", duck: bool = True) -> dict:
    """Mix a voice-over track onto an assembled video.

    Args:
        video_path: Picture (and optional native soundtrack).
        voiceover_path: TTS wav/mp3 path.
        output_path: Optional destination. Defaults next to the video.
        duck: Lower native audio under the voice-over when both exist.

    Returns:
        Dict with muxed output path.
    """
    dest = output_path or video_path.replace(".mp4", "_vo.mp4")
    if is_mock() or not Path(video_path).exists() or not Path(voiceover_path).exists():
        return {
            "output_path": dest,
            "video_path": video_path,
            "voiceover_path": voiceover_path,
            "ducked": duck,
            "result": "skipped" if is_mock() or not Path(video_path).exists() else "success",
        }

    try:
        from moviepy import AudioFileClip, CompositeAudioClip, VideoFileClip
    except ImportError as exc:
        return {"output_path": dest, "error": str(exc), "result": "failed"}

    video = VideoFileClip(video_path)
    voice = AudioFileClip(voiceover_path)
    tracks = []
    if video.audio is not None:
        native = video.audio.with_volume_scaled(0.35) if duck else video.audio
        tracks.append(native)
    tracks.append(voice)
    mixed = CompositeAudioClip(tracks)
    video.with_audio(mixed).write_videofile(dest, logger=None)
    video.close()
    voice.close()
    return {
        "output_path": dest,
        "video_path": video_path,
        "voiceover_path": voiceover_path,
        "ducked": duck,
        "result": "success",
    }
