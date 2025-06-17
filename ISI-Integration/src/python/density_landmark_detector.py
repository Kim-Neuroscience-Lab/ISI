#!/usr/bin/env python3
"""
Density-based geometric landmark detector for mouse models.
Uses cross-sectional density analysis along principal axes to identify anatomical features.
"""

import numpy as np
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DensityLandmarkDetector:
    """Detects mouse anatomical landmarks using density-based analysis."""

    def __init__(self):
        self.vertices = None
        self.faces = None
        self.centroid = None
        self.principal_axes = None
        self.landmarks = {}

    def detect_landmarks(
        self, vertices: np.ndarray, faces: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Main detection method using density-based approach."""
        try:
            logger.info("Starting density-based landmark detection")

            # Store mesh data
            self.vertices = np.array(vertices)
            self.faces = faces
            self.landmarks = {}

            # Step 1: Find mesh centroid and principal axes using PCA
            self._analyze_mesh_geometry()

            # Step 2: Find nose and tail using density analysis
            self._detect_nose_and_tail_by_density()

            logger.info("Density-based landmark detection completed successfully")
            return self._format_results()

        except Exception as e:
            logger.error(f"Density-based landmark detection failed: {e}")
            raise

    def _analyze_mesh_geometry(self):
        """Analyze overall mesh geometry using PCA."""
        logger.info("Analyzing mesh geometry with PCA")

        if self.vertices is None:
            raise ValueError("No vertices available for analysis")

        # Calculate centroid
        self.centroid = np.mean(self.vertices, axis=0)
        logger.info(f"Mesh centroid: {self.centroid}")

        # Center vertices for PCA
        centered_vertices = self.vertices - self.centroid

        # Compute covariance matrix and perform PCA
        covariance_matrix = np.cov(centered_vertices.T)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

        # Sort by eigenvalue (largest first)
        sort_indices = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[sort_indices]
        eigenvectors = eigenvectors[:, sort_indices]

        self.principal_axes = eigenvectors.T  # Each row is a principal axis

        logger.info(f"Principal axis eigenvalues: {eigenvalues}")
        logger.info(f"Primary axis: {self.principal_axes[0]}")

    def _detect_nose_and_tail_by_density(self):
        """Detect nose and tail using cross-sectional density analysis."""
        logger.info("Detecting nose and tail using density analysis")

        if (
            self.principal_axes is None
            or self.vertices is None
            or self.centroid is None
        ):
            raise ValueError("Missing required data for density-based detection")

        # Use the first principal axis as our analysis direction
        primary_axis = self.principal_axes[0]

        # Project all vertices onto the first principal axis
        projections = np.dot(self.vertices - self.centroid, primary_axis)
        min_proj, max_proj = np.min(projections), np.max(projections)

        logger.info(f"Primary axis projection range: {min_proj:.3f} to {max_proj:.3f}")

        # Create slices along the primary axis to analyze cross-sectional density
        num_slices = 40  # Number of slices to analyze
        slice_positions = np.linspace(min_proj, max_proj, num_slices)
        slice_thickness = (max_proj - min_proj) / (
            num_slices * 1.5
        )  # Overlapping slices

        slice_densities = []
        slice_centers = []
        slice_vertex_counts = []

        # Calculate density for each slice
        for slice_pos in slice_positions:
            # Find vertices within this slice
            distances_to_slice = np.abs(projections - slice_pos)
            slice_vertices = self.vertices[distances_to_slice <= slice_thickness]

            if len(slice_vertices) > 5:  # Need minimum vertices for reliable analysis
                # Calculate cross-sectional properties
                slice_center_3d = self.centroid + slice_pos * primary_axis
                distances_from_axis = []

                for v in slice_vertices:
                    # Distance from vertex to axis line through slice center
                    to_vertex = v - slice_center_3d
                    projected_on_axis = np.dot(to_vertex, primary_axis) * primary_axis
                    perpendicular = to_vertex - projected_on_axis
                    distances_from_axis.append(np.linalg.norm(perpendicular))

                # Calculate density metrics
                vertex_count = len(slice_vertices)
                avg_radius = np.mean(distances_from_axis) if distances_from_axis else 0
                max_radius = np.max(distances_from_axis) if distances_from_axis else 0

                # Effective cross-sectional area (using max radius for more stable measure)
                cross_sectional_area = (
                    np.pi * (max_radius**2) if max_radius > 0 else 1e-6
                )
                density = vertex_count / cross_sectional_area

                slice_densities.append(density)
                slice_centers.append(slice_pos)
                slice_vertex_counts.append(vertex_count)

        slice_densities = np.array(slice_densities)
        slice_centers = np.array(slice_centers)
        slice_vertex_counts = np.array(slice_vertex_counts)

        if len(slice_densities) < 10:
            logger.warning(
                "Insufficient slices for density analysis, falling back to extremes"
            )
            self._fallback_to_extremes(projections)
            return

        logger.info(f"Analyzed {len(slice_densities)} slices along primary axis")
        logger.info(
            f"Density range: {np.min(slice_densities):.2f} to {np.max(slice_densities):.2f}"
        )
        logger.info(
            f"Vertex count range: {np.min(slice_vertex_counts)} to {np.max(slice_vertex_counts)}"
        )

        # Smooth the density curve to reduce noise
        window_size = max(3, len(slice_densities) // 8)
        smoothed_densities = np.convolve(
            slice_densities, np.ones(window_size) / window_size, mode="same"
        )

        # Find the sharpest density increase (tail to body transition)
        density_gradients = np.diff(smoothed_densities)

        # Find the steepest positive gradient (biggest density increase)
        max_gradient_idx = np.argmax(density_gradients)
        tail_body_transition_pos = slice_centers[max_gradient_idx]

        logger.info(
            f"Tail-body transition detected at position: {tail_body_transition_pos:.3f}"
        )
        logger.info(f"Max density gradient: {density_gradients[max_gradient_idx]:.3f}")

        # Partition into regions based on transition point
        tail_side_mask = slice_centers <= tail_body_transition_pos
        body_side_mask = slice_centers > tail_body_transition_pos

        if np.sum(tail_side_mask) > 2 and np.sum(body_side_mask) > 2:
            tail_side_avg_density = np.mean(smoothed_densities[tail_side_mask])
            body_side_avg_density = np.mean(smoothed_densities[body_side_mask])

            logger.info(f"Tail side avg density: {tail_side_avg_density:.3f}")
            logger.info(f"Body side avg density: {body_side_avg_density:.3f}")

            # The side with lower average density should be the tail
            if tail_side_avg_density < body_side_avg_density:
                tail_region_center = np.mean(slice_centers[tail_side_mask])
                head_region_center = np.mean(slice_centers[body_side_mask])
                logger.info("Lower density side identified as tail region")
            else:
                tail_region_center = np.mean(slice_centers[body_side_mask])
                head_region_center = np.mean(slice_centers[tail_side_mask])
                logger.info("Higher density side identified as tail region (swapped)")
        else:
            logger.warning("Could not reliably partition into tail/body regions")
            self._fallback_to_extremes(projections)
            return

        # Find actual extreme points in each region
        region_tolerance = (
            max_proj - min_proj
        ) * 0.25  # Look within 25% of each region

        # Nose: most extreme point in the head region
        head_region_mask = np.abs(projections - head_region_center) <= region_tolerance
        if np.sum(head_region_mask) > 0:
            head_candidates = self.vertices[head_region_mask]
            head_projections = projections[head_region_mask]

            # Find the most extreme point in head region
            if head_region_center > tail_region_center:
                nose_idx = np.argmax(head_projections)
            else:
                nose_idx = np.argmin(head_projections)
            nose_point = head_candidates[nose_idx]
        else:
            logger.warning("No vertices found in head region, using global extreme")
            nose_point = self.vertices[
                (
                    np.argmax(projections)
                    if head_region_center > tail_region_center
                    else np.argmin(projections)
                )
            ]

        # Tail tip: most extreme point in the tail region
        tail_region_mask = np.abs(projections - tail_region_center) <= region_tolerance
        if np.sum(tail_region_mask) > 0:
            tail_candidates = self.vertices[tail_region_mask]
            tail_projections = projections[tail_region_mask]

            # Find the most extreme point in tail region
            if tail_region_center < head_region_center:
                tail_idx = np.argmin(tail_projections)
            else:
                tail_idx = np.argmax(tail_projections)
            tail_point = tail_candidates[tail_idx]
        else:
            logger.warning("No vertices found in tail region, using global extreme")
            tail_point = self.vertices[
                (
                    np.argmin(projections)
                    if tail_region_center < head_region_center
                    else np.argmax(projections)
                )
            ]

        # Store landmarks
        self.landmarks["nose"] = nose_point.tolist()
        self.landmarks["tail_tip"] = tail_point.tolist()

        # Find tail attachment point (at the density transition)
        tail_attachment_3d = self.centroid + tail_body_transition_pos * primary_axis
        distances_to_attachment = np.linalg.norm(
            self.vertices - tail_attachment_3d, axis=1
        )
        attachment_idx = np.argmin(distances_to_attachment)
        self.landmarks["tail_attachment"] = self.vertices[attachment_idx].tolist()

        logger.info(f"Nose detected at: {self.landmarks['nose']}")
        logger.info(f"Tail tip at: {self.landmarks['tail_tip']}")
        logger.info(
            f"Tail attachment (density transition) at: {self.landmarks['tail_attachment']}"
        )

        # Verify our classification
        nose_to_center = np.linalg.norm(
            np.array(self.landmarks["nose"]) - self.centroid
        )
        tail_to_center = np.linalg.norm(
            np.array(self.landmarks["tail_tip"]) - self.centroid
        )
        logger.info(f"Nose distance from centroid: {nose_to_center:.3f}")
        logger.info(f"Tail distance from centroid: {tail_to_center:.3f}")

    def _fallback_to_extremes(self, projections):
        """Fallback method using simple extremes."""
        logger.info("Using fallback method: simple PCA extremes")

        min_idx = np.argmin(projections)
        max_idx = np.argmax(projections)

        # Just assign based on projection values (may need manual verification)
        self.landmarks["nose"] = self.vertices[
            max_idx
        ].tolist()  # Assume higher projection is nose
        self.landmarks["tail_tip"] = self.vertices[min_idx].tolist()

        # Simple tail attachment (midpoint)
        nose_point = np.array(self.landmarks["nose"])
        tail_point = np.array(self.landmarks["tail_tip"])
        tail_attachment = nose_point + 0.7 * (tail_point - nose_point)
        self.landmarks["tail_attachment"] = tail_attachment.tolist()

    def _format_results(self) -> Dict[str, Any]:
        """Format detection results."""
        return {
            "landmarks": self.landmarks,
            "metadata": {
                "detection_method": "density_analysis",
                "coordinate_system": "mesh_relative",
                "centroid": (
                    self.centroid.tolist() if self.centroid is not None else None
                ),
                "principal_axes": (
                    self.principal_axes.tolist()
                    if self.principal_axes is not None
                    else None
                ),
                "landmarks_detected": list(self.landmarks.keys()),
                "vertex_count": len(self.vertices) if self.vertices is not None else 0,
            },
        }


# Test with sample data if run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Load and test with mouse STL
    stl_path = Path(__file__).parent.parent / "renderer" / "Mouse.stl"

    if stl_path.exists():
        try:
            from stl import mesh

            logger.info(f"Loading STL from: {stl_path}")

            mouse_mesh = mesh.Mesh.from_file(str(stl_path))
            vertices = mouse_mesh.vectors.reshape(-1, 3)

            # Remove duplicate vertices for cleaner analysis
            unique_vertices = np.unique(vertices, axis=0)
            logger.info(f"Loaded {len(unique_vertices)} unique vertices")

            detector = DensityLandmarkDetector()
            results = detector.detect_landmarks(unique_vertices)

            print("\n=== DENSITY-BASED LANDMARK DETECTION RESULTS ===")
            for landmark_name, position in results["landmarks"].items():
                print(
                    f"{landmark_name}: [{position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}]"
                )

        except ImportError:
            logger.error("numpy-stl not installed. Install with: pip install numpy-stl")
    else:
        logger.error(f"STL file not found: {stl_path}")
        # List available files for debugging
        parent_dir = stl_path.parent
        if parent_dir.exists():
            logger.info(f"Files in {parent_dir}:")
            for file in parent_dir.iterdir():
                if file.suffix.lower() in [".stl", ".obj"]:
                    logger.info(f"  - {file.name}")
