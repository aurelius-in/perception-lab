from __future__ import annotations

# Placeholder ROS bridge message schemas (conceptual)
CAMERA_TOPIC = "/perceptionlab/camera"
DETECTIONS_TOPIC = "/perceptionlab/detections"
TRACKS_TOPIC = "/perceptionlab/tracks"


def publish_stub(topic: str, message: dict) -> None:
    """Replace with ROS publisher integration (rospy/rclpy)."""
    _ = (topic, message)
    # No-op


