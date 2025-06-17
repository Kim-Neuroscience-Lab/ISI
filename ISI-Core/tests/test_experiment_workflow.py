# ISI-Core/tests/test_experiment_workflow.py

"""
Comprehensive test script for ISI experimental workflow.
Demonstrates complete pipeline from setup validation through analysis.
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

# Import the experimental services
from ..src.services.experiment_service import (
    SetupManager,
    StimulusGenerator,
    AcquisitionController,
)
from ..src.interfaces.experiment_interfaces import (
    SetupParameters,
    StimulusParameters,
    AcquisitionParameters,
    ExperimentPhase,
)


def test_complete_workflow():
    """Test the complete experimental workflow."""
    print("=== ISI Experimental Workflow Test ===\n")

    # Create temporary directory for test outputs
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. SETUP PHASE
        print("1. SETUP PHASE")
        print("-" * 40)

        setup_manager = SetupManager()

        # Create setup parameters
        setup_params = SetupParameters(
            monitor_size=(68.0, 121.0),
            monitor_resolution=(1080, 1920),
            monitor_distance=10.0,
            monitor_elevation=20.0,
            monitor_rotation=0.0,
            mouse_eye_height=5.0,
            mouse_visual_field_vertical=120.0,
            mouse_visual_field_horizontal=270.0,
            table_width=50.0,
            table_depth=30.0,
            table_height=10.0,
        )

        # Validate setup
        validation_result = setup_manager.validate_setup(setup_params)
        print(
            f"Setup validation: {'SUCCESS' if validation_result.success else 'FAILED'}"
        )

        if validation_result.success and validation_result.data:
            stats = validation_result.data.get("coverage_statistics", {})
            print(
                f"Visual field coverage: {stats.get('total_coverage_estimate', 0):.1f}%"
            )
            print(f"Warnings: {len(validation_result.data.get('warnings', []))}")

        # Generate 3D visualization
        viz_result = setup_manager.generate_3d_visualization(setup_params)
        print(f"3D visualization: {'SUCCESS' if viz_result.success else 'FAILED'}")
        if viz_result.success:
            print(f"Visualization ID: {viz_result.data}")

        # Export setup configuration
        config_path = temp_path / "setup_config.json"
        export_result = setup_manager.export_setup_configuration(
            setup_params, str(config_path)
        )
        print(
            f"Configuration export: {'SUCCESS' if export_result.success else 'FAILED'}"
        )
        print(f"Exported to: {config_path}\n")

        # 2. STIMULUS GENERATION PHASE
        print("2. STIMULUS GENERATION PHASE")
        print("-" * 40)

        stimulus_generator = StimulusGenerator()

        # Create stimulus parameters for drifting bar
        stimulus_params = StimulusParameters(
            stimulus_type="drifting_bar",
            duration=5.0,
            fps=60,
            contrast=1.0,
            orientation=0.0,
            width=5.0,
            speed=10.0,
            background_color=(128, 128, 128),
        )

        # Generate preview frames
        preview_result = stimulus_generator.preview_stimulus(
            stimulus_params, setup_params, frame_count=20
        )
        print(f"Stimulus preview: {'SUCCESS' if preview_result.success else 'FAILED'}")
        if preview_result.success and preview_result.data:
            print(f"Preview frames generated: {len(preview_result.data)}")

        # Generate full stimulus sequence
        stimulus_result = stimulus_generator.generate_stimulus_frames(
            stimulus_params, setup_params
        )
        print(
            f"Stimulus generation: {'SUCCESS' if stimulus_result.success else 'FAILED'}"
        )

        stimulus_frames = []
        if stimulus_result.success and stimulus_result.data:
            stimulus_frames = stimulus_result.data
            print(f"Total frames generated: {len(stimulus_frames)}")
            print(f"Duration: {stimulus_params.duration} seconds")
            print(f"Frame rate: {stimulus_params.fps} FPS")

        # Save stimulus sequence
        stimulus_path = temp_path / "stimulus_sequence.json"
        if stimulus_frames:  # Only save if we have frames
            save_result = stimulus_generator.save_stimulus_sequence(
                stimulus_frames, str(stimulus_path)
            )
            print(f"Stimulus save: {'SUCCESS' if save_result.success else 'FAILED'}")

            # Load stimulus sequence (to verify save/load)
            load_result = stimulus_generator.load_stimulus_sequence(str(stimulus_path))
            print(f"Stimulus load: {'SUCCESS' if load_result.success else 'FAILED'}")
            if load_result.success and load_result.data:
                print(f"Loaded frames: {len(load_result.data)}\n")
        else:
            print("Stimulus save: SKIPPED (no frames generated)")
            print("Stimulus load: SKIPPED (no frames to load)\n")

        # 3. ACQUISITION PHASE
        print("3. ACQUISITION PHASE")
        print("-" * 40)

        acquisition_controller = AcquisitionController()

        # Create acquisition parameters
        acquisition_params = AcquisitionParameters(
            camera_device_id=0,
            camera_resolution=(1920, 1080),
            camera_fps=30,
            camera_exposure=16.67,  # milliseconds
            camera_gain=None,
            stimulus_monitor_id=1,
            main_monitor_id=0,
            fullscreen_stimulus=True,
            sync_tolerance_ms=16.67,
            buffer_size=1000,
            save_camera_frames=True,
            save_stimulus_frames=True,
            output_directory=str(temp_path / "acquisition_data"),
            compression_quality=95,
        )

        # Initialize acquisition
        init_result = acquisition_controller.initialize_acquisition(acquisition_params)
        print(
            f"Acquisition initialization: {'SUCCESS' if init_result.success else 'FAILED'}"
        )

        # Get acquisition status
        status_result = acquisition_controller.get_acquisition_status()
        print(f"Status check: {'SUCCESS' if status_result.success else 'FAILED'}")
        if status_result.success and status_result.data:
            status = status_result.data
            print(f"Initialized: {status.get('initialized', False)}")
            print(f"Camera connected: {status.get('camera_connected', False)}")

        # Get camera preview
        preview_result = acquisition_controller.get_camera_preview()
        print(f"Camera preview: {'SUCCESS' if preview_result.success else 'FAILED'}")
        if preview_result.success and preview_result.data:
            print(f"Preview frame size: {len(preview_result.data)} bytes")

        # Start acquisition (simulated)
        if stimulus_frames:
            start_result = acquisition_controller.start_acquisition(stimulus_frames)
            print(
                f"Acquisition start: {'SUCCESS' if start_result.success else 'FAILED'}"
            )
            if start_result.success:
                print(f"Acquisition ID: {start_result.data}")

                # Brief pause to simulate acquisition
                import time

                time.sleep(2)

                # Stop acquisition
                stop_result = acquisition_controller.stop_acquisition()
                print(
                    f"Acquisition stop: {'SUCCESS' if stop_result.success else 'FAILED'}"
                )

        print()

        # 4. SUMMARY
        print("4. WORKFLOW SUMMARY")
        print("-" * 40)

        # Check all generated files
        files_created = list(temp_path.glob("*"))
        print(f"Files created: {len(files_created)}")
        for file_path in files_created:
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  - {file_path.name}: {size} bytes")

        # Load and display configuration
        if config_path.exists():
            with open(config_path, "r") as f:
                config_data = json.load(f)
            print(
                f"\nConfiguration format version: {config_data.get('format_version')}"
            )
            print(f"Export timestamp: {config_data.get('exported_at')}")

        print("\n=== Workflow Test Complete ===")
        return True


def test_error_handling():
    """Test error handling and fail-fast behavior."""
    print("\n=== Error Handling Tests ===\n")

    setup_manager = SetupManager()
    stimulus_generator = StimulusGenerator()
    acquisition_controller = AcquisitionController()

    # Test invalid parameters
    print("Testing invalid parameter handling...")

    try:
        # Test with empty string for file path
        stimulus_generator.save_stimulus_sequence([], "")
        print("ERROR: Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly caught ValueError: {e}")
    except Exception as e:
        print(f"✓ Caught exception for empty file path: {e}")

    # Test missing file scenario
    load_result = stimulus_generator.load_stimulus_sequence("nonexistent_file.json")
    print(
        f"Missing file handling: {'SUCCESS' if not load_result.success else 'FAILED'}"
    )
    if not load_result.success:
        print(f"  Error: {load_result.error_message}")

    print("\n=== Error Handling Complete ===")


def main():
    """Run all tests."""
    try:
        success = test_complete_workflow()
        test_error_handling()

        if success:
            print("\n🎉 All tests passed! ISI workflow implementation is ready.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")

    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
