"""
Pure Geometric Landmark Detection Service

This module provides orientation-independent landmark detection for mouse models
using only geometric relationships and proper mathematical analysis.

Key Principles:
- NO world coordinate assumptions (no hardcoded X, Y, Z axes)
- NO positional assumptions (no "up", "down", "left", "right")
- Pure geometric analysis using PCA, distance relationships, and surface analysis
- Robust to arbitrary mouse orientations and poses
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from scipy.spatial.distance import pdist, squareform
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)


class GeometricLandmarkDetector:
    """
    Pure geometric landmark detector that works regardless of mouse orientation.

    Uses only:
    - Principal Component Analysis (PCA) to find natural mesh axes
    - Distance and surface curvature analysis
    - Bilateral symmetry detection
    - Cross-sectional area analysis along mesh-derived axes
    """

    def __init__(self):
        self.vertices: Optional[np.ndarray] = None
        self.faces: Optional[np.ndarray] = None
        self.principal_axes: Optional[np.ndarray] = None
        self.centroid: Optional[np.ndarray] = None
        self.landmarks: Dict[str, Any] = {}

    def detect_landmarks(
        self, vertices: np.ndarray, faces: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Detect anatomical landmarks using pure geometric analysis.

        Args:
            vertices: Nx3 array of mesh vertices
            faces: Optional face connectivity for surface analysis

        Returns:
            Dictionary containing detected landmark positions and metadata
        """
        logger.info(
            f"Starting pure geometric landmark detection on {len(vertices)} vertices"
        )

        # Validate input
        if vertices.shape[1] != 3:
            raise ValueError(f"Vertices must be Nx3 array, got {vertices.shape}")

        self.vertices = vertices.copy()
        self.faces = faces
        self.landmarks = {}

        try:
            # Step 1: Find mesh centroid and principal axes using PCA
            self._analyze_mesh_geometry()

            # Step 2: Find nose and tail using cross-sectional area analysis
            self._detect_nose_and_tail()

            # Step 3: Find ears using lateral protrusion analysis
            # self._detect_ears()

            # Step 4: Find feet using simple mesh extrema analysis
            # self._detect_feet()

            # Step 5: Skip whiskers (too slow for real-time use)
            # self._detect_whiskers()

            # Step 6: Calculate derived landmarks (eye center, etc.)
            # self._calculate_derived_landmarks()

            logger.info("Geometric landmark detection completed successfully")
            return self._format_results()

        except Exception as e:
            logger.error(f"Geometric landmark detection failed: {e}")
            raise

    def _analyze_mesh_geometry(self):
        """Analyze overall mesh geometry using PCA."""
        logger.info("Analyzing mesh geometry with PCA")

        if self.vertices is None:
            raise ValueError("No vertices available for analysis")

        # Calculate centroid
        self.centroid = np.mean(self.vertices, axis=0)
        logger.info(f"Mesh centroid: {self.centroid}")

        # Center vertices
        centered_vertices = self.vertices - self.centroid

        # Perform PCA to find principal axes
        pca = PCA(n_components=3)
        pca.fit(centered_vertices)

        # Store principal axes (already normalized)
        self.principal_axes = pca.components_
        explained_variance = pca.explained_variance_ratio_

        logger.info(f"Principal axes found with variance ratios: {explained_variance}")
        logger.info(f"Primary axis (longest): {self.principal_axes[0]}")
        logger.info(f"Secondary axis: {self.principal_axes[1]}")
        logger.info(f"Tertiary axis: {self.principal_axes[2]}")

        # Validate PCA results
        if explained_variance[0] < 0.3:
            logger.warning(f"Low primary axis variance: {explained_variance[0]:.3f}")

    def _detect_nose_and_tail(self):
        """Detect nose and tail using PCA extremes along first principal axis."""
        logger.info("Detecting nose and tail using PCA extremes")

        if (
            self.principal_axes is None
            or self.vertices is None
            or self.centroid is None
        ):
            raise ValueError("Missing required data for nose/tail detection")

        # Use the first principal axis (nose-to-tail direction)
        primary_axis = self.principal_axes[0]

        # Project all vertices onto the first principal axis
        projections = np.dot(self.vertices - self.centroid, primary_axis)

        # Find the actual extreme points along this axis
        min_proj_idx = np.argmin(projections)
        max_proj_idx = np.argmax(projections)

        extreme1_point = self.vertices[min_proj_idx]  # One end
        extreme2_point = self.vertices[max_proj_idx]  # Other end

        logger.info(
            f"Primary axis projection range: {np.min(projections):.3f} to {np.max(projections):.3f}"
        )
        logger.info(f"Extreme points: end1={extreme1_point}, end2={extreme2_point}")

        # Determine which is nose vs tail using multiple criteria
        # 1. Local point density (nose is typically sharper - fewer nearby vertices)
        # 2. Local curvature (nose is typically more pointed)
        # 3. Cross-sectional area (nose typically has smaller cross-section)

        mesh_size = np.linalg.norm(
            np.max(self.vertices, axis=0) - np.min(self.vertices, axis=0)
        )
        search_radius = mesh_size * 0.03  # 3% of mesh size

        # Count nearby vertices for each extreme (local density)
        distances1 = np.linalg.norm(self.vertices - extreme1_point, axis=1)
        nearby1_count = np.sum(distances1 <= search_radius)

        distances2 = np.linalg.norm(self.vertices - extreme2_point, axis=1)
        nearby2_count = np.sum(distances2 <= search_radius)

        # Calculate local "sharpness" - how quickly the cross-sectional area changes
        def calculate_sharpness(extreme_point, axis_direction):
            # Sample points along the axis from the extreme
            step_size = mesh_size * 0.02  # 2% steps
            sharpness_samples = []

            for i in range(1, 4):  # Check 3 points inward from extreme
                sample_point = extreme_point + (axis_direction * step_size * i)
                # Find vertices within a thin slice at this point
                slice_thickness = mesh_size * 0.01

                # Project all vertices onto the axis through sample_point
                if self.vertices is not None:
                    projected_dists = np.abs(
                        np.dot(self.vertices - sample_point, axis_direction)
                    )
                    slice_vertices = self.vertices[projected_dists <= slice_thickness]
                else:
                    continue

                if len(slice_vertices) > 0:
                    # Calculate cross-sectional "radius" at this slice
                    distances_from_axis = []
                    for v in slice_vertices:
                        # Distance from vertex to axis line
                        to_vertex = v - sample_point
                        projected = np.dot(to_vertex, axis_direction) * axis_direction
                        perpendicular = to_vertex - projected
                        distances_from_axis.append(np.linalg.norm(perpendicular))

                    avg_radius = np.mean(distances_from_axis)
                    sharpness_samples.append(avg_radius)

            # Sharpness = how quickly radius increases from tip
            if len(sharpness_samples) >= 2:
                radius_increase_rate = np.mean(np.diff(sharpness_samples))
                return radius_increase_rate
            return 0

        # Calculate sharpness for both extremes
        # For extreme1, look inward along primary axis
        axis_direction1 = (extreme2_point - extreme1_point) / np.linalg.norm(
            extreme2_point - extreme1_point
        )
        sharpness1 = calculate_sharpness(extreme1_point, axis_direction1)

        # For extreme2, look inward along primary axis (opposite direction)
        axis_direction2 = (extreme1_point - extreme2_point) / np.linalg.norm(
            extreme1_point - extreme2_point
        )
        sharpness2 = calculate_sharpness(extreme2_point, axis_direction2)

        logger.info(
            f"Local vertex density: extreme1={nearby1_count}, extreme2={nearby2_count}"
        )
        logger.info(
            f"Sharpness scores: extreme1={sharpness1:.4f}, extreme2={sharpness2:.4f}"
        )

        # Decision logic: nose should have BOTH lower density AND higher sharpness
        density_score1 = -nearby1_count  # Lower density = higher score
        density_score2 = -nearby2_count

        sharpness_score1 = sharpness1  # Higher sharpness = higher score
        sharpness_score2 = sharpness2

        # Combined score (both criteria must agree for confidence)
        combined_score1 = density_score1 + (sharpness_score1 * 1000)  # Scale sharpness
        combined_score2 = density_score2 + (sharpness_score2 * 1000)

        logger.info(
            f"Combined scores: extreme1={combined_score1:.2f}, extreme2={combined_score2:.2f}"
        )

        # Higher combined score = more likely to be nose
        if combined_score1 > combined_score2:
            nose_point = extreme1_point
            tail_point = extreme2_point
            logger.info("Extreme1 (higher combined score) classified as nose")
        else:
            nose_point = extreme2_point
            tail_point = extreme1_point
            logger.info("Extreme2 (higher combined score) classified as nose")

        # Verify the choice makes sense by checking if nose is actually "pointier"
        nose_density = (
            nearby1_count
            if np.array_equal(nose_point, extreme1_point)
            else nearby2_count
        )
        tail_density = (
            nearby2_count
            if np.array_equal(nose_point, extreme1_point)
            else nearby1_count
        )

        if nose_density > tail_density:
            logger.warning(
                f"⚠️  Nose has higher density than tail ({nose_density} vs {tail_density}) - this may indicate incorrect classification"
            )
            # If density check fails, try swapping
            logger.info(
                "🔄 Swapping nose and tail classification based on density check"
            )
            nose_point, tail_point = tail_point, nose_point

        # Store landmarks
        self.landmarks["nose"] = nose_point.tolist()
        self.landmarks["tail_tip"] = tail_point.tolist()

        # Find tail attachment point (70% from nose toward tail)
        tail_attachment = nose_point + 0.7 * (tail_point - nose_point)
        self.landmarks["tail_attachment"] = tail_attachment.tolist()

        logger.info(f"Nose detected at: {self.landmarks['nose']}")
        logger.info(f"Tail tip at: {self.landmarks['tail_tip']}")
        logger.info(f"Tail attachment at: {self.landmarks['tail_attachment']}")

    def _detect_ears(self):
        """Detect ears using bilateral lateral protrusion analysis."""
        logger.info("Detecting ears using bilateral analysis")

        if "nose" not in self.landmarks:
            logger.warning("Cannot detect ears without nose landmark")
            return

        if self.vertices is None or self.principal_axes is None:
            raise ValueError(
                "No vertices or principal axes available for ear detection"
            )

        nose = np.array(self.landmarks["nose"])

        # Use primary axis directly for head orientation
        primary_axis = self.principal_axes[0]

        # Define a much smaller head region for ear detection
        mesh_size = np.linalg.norm(
            np.max(self.vertices, axis=0) - np.min(self.vertices, axis=0)
        )
        head_region_radius = (
            mesh_size * 0.15
        )  # Much smaller region (15% instead of 30%)

        # Filter to head region vertices using efficient numpy operations
        distances_from_nose = np.linalg.norm(self.vertices - nose, axis=1)
        head_mask = distances_from_nose <= head_region_radius
        head_vertices_array = self.vertices[head_mask]

        if len(head_vertices_array) < 10:
            logger.warning(
                f"Insufficient head vertices for ear detection: {len(head_vertices_array)}"
            )
            return

        logger.info(f"Analyzing {len(head_vertices_array)} vertices in head region")

        # Simple ear detection: find extremes perpendicular to primary axis
        # Use secondary axis (from PCA) as the left-right direction
        secondary_axis = self.principal_axes[1]

        # Project head vertices onto secondary axis to find left/right extremes
        projections = np.dot(head_vertices_array - nose, secondary_axis)

        # Find left and right extremes
        left_idx = np.argmin(projections)
        right_idx = np.argmax(projections)

        left_ear = head_vertices_array[left_idx]
        right_ear = head_vertices_array[right_idx]

        # Store landmarks
        self.landmarks["left_ear"] = left_ear.tolist()
        self.landmarks["right_ear"] = right_ear.tolist()

        logger.info(f"Left ear detected at: {self.landmarks['left_ear']}")
        logger.info(f"Right ear detected at: {self.landmarks['right_ear']}")

    def _find_lateral_protrusions(
        self, vertices: np.ndarray, reference_point: np.ndarray, axis: np.ndarray
    ) -> List[np.ndarray]:
        """Find lateral protrusions (features extending perpendicular to main axis)."""

        protrusions = []
        neighborhood_radius = (
            np.linalg.norm(np.max(vertices, axis=0) - np.min(vertices, axis=0)) * 0.1
        )

        for i, vertex in enumerate(vertices):
            # Calculate lateral distance (perpendicular to axis)
            ref_to_vertex = vertex - reference_point
            axial_component = np.dot(ref_to_vertex, axis) * axis
            lateral_component = ref_to_vertex - axial_component
            lateral_distance = np.linalg.norm(lateral_component)

            # Check if this is a local maximum in lateral distance
            neighbors = vertices[
                np.linalg.norm(vertices - vertex, axis=1) <= neighborhood_radius
            ]

            if len(neighbors) < 3:
                continue

            # Calculate lateral distances for neighbors
            neighbor_lateral_distances = []
            for neighbor in neighbors:
                neighbor_ref = neighbor - reference_point
                neighbor_axial = np.dot(neighbor_ref, axis) * axis
                neighbor_lateral = neighbor_ref - neighbor_axial
                neighbor_lateral_distances.append(np.linalg.norm(neighbor_lateral))

            # Check if this vertex is a local maximum
            if (
                lateral_distance >= np.max(neighbor_lateral_distances) * 0.98
            ):  # 98% threshold for robustness
                protrusions.append(vertex)

        # Sort by lateral distance (most protruding first)
        if protrusions:
            protrusions_array = np.array(protrusions)
            lateral_distances = []
            for vertex in protrusions_array:
                ref_to_vertex = vertex - reference_point
                axial_component = np.dot(ref_to_vertex, axis) * axis
                lateral_component = ref_to_vertex - axial_component
                lateral_distances.append(np.linalg.norm(lateral_component))

            sorted_indices = np.argsort(lateral_distances)[::-1]  # Descending order
            protrusions = [protrusions_array[i] for i in sorted_indices]

        return protrusions

    def _separate_bilateral_features(
        self,
        features: np.ndarray,
        reference_point: np.ndarray,
        primary_axis: np.ndarray,
    ) -> Dict[str, Optional[np.ndarray]]:
        """Separate features into left/right using bilateral symmetry."""

        if len(features) < 2:
            return {"left": None, "right": None}

        # Create a perpendicular axis for left/right separation
        # Use the secondary principal axis if available, otherwise use geometric approach
        if self.principal_axes is not None:
            lateral_axis = self.principal_axes[1]  # Secondary principal axis
        else:
            # Create perpendicular using cross product with centroid direction
            if self.centroid is None:
                raise ValueError("No centroid available for bilateral separation")
            to_centroid = self.centroid - reference_point
            to_centroid_norm = to_centroid / np.linalg.norm(to_centroid)
            lateral_axis = np.cross(primary_axis, to_centroid_norm)
            lateral_axis = lateral_axis / np.linalg.norm(lateral_axis)

        # Project features onto lateral axis
        lateral_projections = []
        for feature in features:
            ref_to_feature = feature - reference_point
            projection = np.dot(ref_to_feature, lateral_axis)
            lateral_projections.append(projection)

        lateral_projections = np.array(lateral_projections)

        # Separate into left (negative) and right (positive)
        left_indices = lateral_projections < -0.01  # Small threshold for noise
        right_indices = lateral_projections > 0.01

        left_features = features[left_indices] if np.any(left_indices) else None
        right_features = features[right_indices] if np.any(right_indices) else None

        # Select best from each side (most lateral)
        left_ear = (
            left_features[np.argmin(lateral_projections[left_indices])]
            if left_features is not None
            else None
        )
        right_ear = (
            right_features[np.argmax(lateral_projections[right_indices])]
            if right_features is not None
            else None
        )

        return {"left": left_ear, "right": right_ear}

    def _detect_feet(self):
        """Detect feet using simple mesh extrema analysis - no vertex iteration."""
        logger.info("Detecting feet using simple mesh extrema analysis")

        if self.vertices is None:
            logger.warning("No vertices available for feet detection")
            return

        # Simple approach: Find mesh bounding box extrema
        vertices = self.vertices

        # Get mesh bounds
        min_coords = np.min(vertices, axis=0)
        max_coords = np.max(vertices, axis=0)

        # Assume standard orientation: X=left-right, Y=up-down, Z=front-back
        # Feet are typically at the bottom (min Y) and spread laterally

        # Find bottom 10% of mesh (where feet should be)
        y_range = max_coords[1] - min_coords[1]
        bottom_threshold = min_coords[1] + 0.1 * y_range

        # Get vertices in bottom region
        bottom_mask = vertices[:, 1] <= bottom_threshold
        bottom_vertices = vertices[bottom_mask]

        if len(bottom_vertices) < 4:
            logger.warning("Insufficient vertices in bottom region for feet detection")
            return

        # Find extrema in bottom region
        bottom_min = np.min(bottom_vertices, axis=0)
        bottom_max = np.max(bottom_vertices, axis=0)

        # Define foot positions at corners of bottom region
        # Front feet: forward positions
        # Back feet: rear positions
        z_mid = (bottom_min[2] + bottom_max[2]) / 2
        front_z = bottom_max[2] - 0.2 * (
            bottom_max[2] - bottom_min[2]
        )  # 20% from front
        back_z = bottom_min[2] + 0.2 * (bottom_max[2] - bottom_min[2])  # 20% from back

        # Left/right positions
        left_x = bottom_min[0] + 0.1 * (
            bottom_max[0] - bottom_min[0]
        )  # 10% from left edge
        right_x = bottom_max[0] - 0.1 * (
            bottom_max[0] - bottom_min[0]
        )  # 10% from right edge

        # Y position (bottom of mesh)
        foot_y = bottom_min[1]

        # Define foot positions
        self.landmarks["front_left_foot"] = [left_x, foot_y, front_z]
        self.landmarks["front_right_foot"] = [right_x, foot_y, front_z]
        self.landmarks["back_left_foot"] = [left_x, foot_y, back_z]
        self.landmarks["back_right_foot"] = [right_x, foot_y, back_z]

        logger.info("Feet detected using simple mesh extrema:")
        logger.info(f"  Front left: {self.landmarks['front_left_foot']}")
        logger.info(f"  Front right: {self.landmarks['front_right_foot']}")
        logger.info(f"  Back left: {self.landmarks['back_left_foot']}")
        logger.info(f"  Back right: {self.landmarks['back_right_foot']}")

    def _detect_whiskers(self):
        """Detect whiskers using fine lateral protrusion analysis in nose region."""
        logger.info("Detecting whiskers using fine protrusion analysis")

        if "nose" not in self.landmarks:
            logger.warning("Cannot detect whiskers without nose landmark")
            return

        if self.vertices is None or self.principal_axes is None:
            raise ValueError("Missing required data for whisker detection")

        nose = np.array(self.landmarks["nose"])

        # Define whisker region (very close to nose)
        whisker_region_extent = 0.15  # 15% of mesh scale
        mesh_scale = np.linalg.norm(
            np.max(self.vertices, axis=0) - np.min(self.vertices, axis=0)
        )
        whisker_radius = mesh_scale * whisker_region_extent

        # Filter to whisker region
        whisker_vertices = self.vertices[
            np.linalg.norm(self.vertices - nose, axis=1) <= whisker_radius
        ]

        if len(whisker_vertices) < 5:
            logger.warning(
                f"Insufficient vertices in whisker region: {len(whisker_vertices)}"
            )
            return

        logger.info(f"Analyzing {len(whisker_vertices)} vertices in whisker region")

        # Find fine lateral protrusions
        if "tail_attachment" in self.landmarks:
            tail_attachment = np.array(self.landmarks["tail_attachment"])
            nose_to_tail = tail_attachment - nose
            nose_to_tail_norm = nose_to_tail / np.linalg.norm(nose_to_tail)
        else:
            # Use primary axis as fallback
            nose_to_tail_norm = self.principal_axes[0]

        whisker_protrusions = self._find_lateral_protrusions(
            whisker_vertices, nose, nose_to_tail_norm
        )

        if len(whisker_protrusions) < 2:
            logger.warning(
                f"Insufficient whisker protrusions found: {len(whisker_protrusions)}"
            )
            return

        # Separate into left/right
        whiskers = self._separate_bilateral_features(
            np.array(whisker_protrusions), nose, nose_to_tail_norm
        )

        # Store multiple whiskers per side if found
        self.landmarks["left_whiskers"] = []
        self.landmarks["right_whiskers"] = []

        # For now, store just the primary whisker per side
        if whiskers["left"] is not None:
            self.landmarks["left_whiskers"] = [whiskers["left"].tolist()]
        if whiskers["right"] is not None:
            self.landmarks["right_whiskers"] = [whiskers["right"].tolist()]

        logger.info(
            f"Whiskers detected: left={len(self.landmarks['left_whiskers'])}, right={len(self.landmarks['right_whiskers'])}"
        )

    def _calculate_derived_landmarks(self):
        """Calculate derived landmarks from primary detections."""
        logger.info("Calculating derived landmarks")

        # Calculate eye center if both ears are detected
        if (
            "left_ear" in self.landmarks
            and "right_ear" in self.landmarks
            and "nose" in self.landmarks
        ):
            nose = np.array(self.landmarks["nose"])
            left_ear = np.array(self.landmarks["left_ear"])
            right_ear = np.array(self.landmarks["right_ear"])

            ear_midpoint = (left_ear + right_ear) / 2
            eye_center = nose + 0.375 * (
                ear_midpoint - nose
            )  # 3/8 of way from nose to ear midpoint

            self.landmarks["eye_center"] = eye_center.tolist()
            logger.info(f"Eye center calculated at: {self.landmarks['eye_center']}")

    def _format_results(self) -> Dict[str, Any]:
        """Format detection results for return to client."""

        # Convert numpy arrays to lists and ensure all coordinates are finite
        formatted_landmarks = {}

        for key, value in self.landmarks.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], list):  # Multiple items (like whiskers)
                    formatted_landmarks[key] = value
                else:  # Single coordinate
                    if len(value) == 3 and all(np.isfinite(value)):
                        formatted_landmarks[key] = value
                    else:
                        logger.warning(f"Invalid landmark {key}: {value}")
            elif value is not None:
                logger.warning(f"Unexpected landmark format for {key}: {value}")

        # Add metadata
        results = {
            "landmarks": formatted_landmarks,
            "metadata": {
                "detection_method": "pure_geometric",
                "coordinate_system": "mesh_relative",
                "principal_axes": (
                    self.principal_axes.tolist()
                    if self.principal_axes is not None
                    else None
                ),
                "centroid": (
                    self.centroid.tolist() if self.centroid is not None else None
                ),
                "vertex_count": len(self.vertices) if self.vertices is not None else 0,
                "landmarks_detected": list(formatted_landmarks.keys()),
            },
        }

        logger.info(f"Formatted results with {len(formatted_landmarks)} landmarks")
        return results
