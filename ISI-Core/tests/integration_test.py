# ISI-Core/tests/integration_test.py

"""
Comprehensive integration test for ISI experimental workflow.
Tests complete system integration with all services and proper error handling.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List

# Import the service factory and all experimental services
from ..src.factories.service_factory import service_factory
from ..src.interfaces.experiment_interfaces import (
    SetupParameters,
    StimulusParameters,
    AcquisitionParameters,
    AnalysisParameters,
    ExperimentPhase,
)


class ISIIntegrationTest:
    """
    Integration test suite for ISI experimental workflow.
    Single Responsibility: Test complete system integration.
    """

    def __init__(self):
        """Initialize integration test suite."""
        self.services = service_factory.create_complete_workflow()
        self.current_experiment_id: str = ""
        self.test_results: Dict[str, bool] = {}

    def run_complete_integration_test(self) -> bool:
        """Run the complete integration test suite."""
        print("=== ISI Experimental Workflow Integration Test ===\n")

        # Test service factory
        self._test_service_factory()

        # Test complete experimental workflow
        self._test_complete_workflow()

        # Test error handling and fail-fast behavior
        self._test_error_handling()

        # Test frame synchronization
        self._test_frame_synchronization()

        # Test data analysis pipeline
        self._test_analysis_pipeline()

        # Print test summary
        self._print_test_summary()

        return all(self.test_results.values())

    def _test_service_factory(self) -> None:
        """Test service factory functionality."""
        print("1. TESTING SERVICE FACTORY")
        print("-" * 40)

        try:
            # Test service registration
            registered_services = service_factory.get_registered_services()
            expected_services = [
                "data_store",
                "configuration",
                "setup_manager",
                "stimulus_generator",
                "acquisition_controller",
                "frame_synchronizer",
                "data_analyzer",
                "experiment_workflow",
            ]

            all_registered = all(
                service in registered_services for service in expected_services
            )
            self.test_results["service_factory_registration"] = all_registered
            print(f"Service registration: {'PASS' if all_registered else 'FAIL'}")

            # Test service creation
            setup_manager = service_factory.get_setup_manager()
            stimulus_generator = service_factory.get_stimulus_generator()
            acquisition_controller = service_factory.get_acquisition_controller()

            services_created = all(
                [
                    setup_manager is not None,
                    stimulus_generator is not None,
                    acquisition_controller is not None,
                ]
            )
            self.test_results["service_factory_creation"] = services_created
            print(f"Service creation: {'PASS' if services_created else 'FAIL'}")

            # Test singleton behavior
            setup_manager_2 = service_factory.get_setup_manager()
            singleton_working = setup_manager is setup_manager_2
            self.test_results["service_factory_singleton"] = singleton_working
            print(f"Singleton pattern: {'PASS' if singleton_working else 'FAIL'}")

        except Exception as e:
            print(f"Service factory test failed: {e}")
            self.test_results["service_factory_registration"] = False
            self.test_results["service_factory_creation"] = False
            self.test_results["service_factory_singleton"] = False

        print()

    def _test_complete_workflow(self) -> None:
        """Test complete experimental workflow from setup to analysis."""
        print("2. TESTING COMPLETE WORKFLOW")
        print("-" * 40)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                # Test experiment creation
                experiment_workflow = self.services["experiment_workflow"]
                setup_params = self._create_test_setup_parameters()

                create_result = experiment_workflow.create_experiment(
                    "Integration Test Experiment", setup_params
                )

                experiment_created = create_result.success and create_result.data
                self.test_results["workflow_experiment_creation"] = experiment_created
                print(
                    f"Experiment creation: {'PASS' if experiment_created else 'FAIL'}"
                )

                if experiment_created:
                    self.current_experiment_id = create_result.data

                # Test setup validation
                setup_manager = self.services["setup_manager"]
                validation_result = setup_manager.validate_setup(setup_params)

                setup_valid = validation_result.success
                self.test_results["workflow_setup_validation"] = setup_valid
                print(f"Setup validation: {'PASS' if setup_valid else 'FAIL'}")

                # Test stimulus generation
                stimulus_generator = self.services["stimulus_generator"]
                stimulus_params = self._create_test_stimulus_parameters()

                stimulus_result = stimulus_generator.generate_stimulus_frames(
                    stimulus_params, setup_params
                )

                stimulus_generated = stimulus_result.success and stimulus_result.data
                self.test_results["workflow_stimulus_generation"] = stimulus_generated
                print(
                    f"Stimulus generation: {'PASS' if stimulus_generated else 'FAIL'}"
                )

                # Test acquisition initialization
                acquisition_controller = self.services["acquisition_controller"]
                acquisition_params = self._create_test_acquisition_parameters(
                    str(temp_path)
                )

                init_result = acquisition_controller.initialize_acquisition(
                    acquisition_params
                )

                acquisition_initialized = init_result.success
                self.test_results["workflow_acquisition_init"] = acquisition_initialized
                print(
                    f"Acquisition initialization: {'PASS' if acquisition_initialized else 'FAIL'}"
                )

                # Test phase transitions
                if self.current_experiment_id:
                    # Transition to stimulus generation
                    transition_result = experiment_workflow.transition_phase(
                        self.current_experiment_id, ExperimentPhase.STIMULUS_GENERATION
                    )

                    phase_transition = transition_result.success
                    self.test_results["workflow_phase_transition"] = phase_transition
                    print(f"Phase transition: {'PASS' if phase_transition else 'FAIL'}")

                # Test workflow validation
                if self.current_experiment_id:
                    validation_result = experiment_workflow.validate_workflow(
                        self.current_experiment_id
                    )

                    workflow_valid = validation_result.success
                    self.test_results["workflow_validation"] = workflow_valid
                    print(
                        f"Workflow validation: {'PASS' if workflow_valid else 'FAIL'}"
                    )

            except Exception as e:
                print(f"Complete workflow test failed: {e}")
                self.test_results["workflow_experiment_creation"] = False
                self.test_results["workflow_setup_validation"] = False
                self.test_results["workflow_stimulus_generation"] = False
                self.test_results["workflow_acquisition_init"] = False
                self.test_results["workflow_phase_transition"] = False
                self.test_results["workflow_validation"] = False

        print()

    def _test_error_handling(self) -> None:
        """Test error handling and fail-fast behavior."""
        print("3. TESTING ERROR HANDLING")
        print("-" * 40)

        try:
            setup_manager = self.services["setup_manager"]
            stimulus_generator = self.services["stimulus_generator"]

            # Test invalid parameter types
            try:
                # This should fail due to type checking
                stimulus_generator.save_stimulus_sequence([], "")
                error_handling_1 = False
            except (ValueError, TypeError) as e:
                error_handling_1 = True
                print(f"✓ Correctly caught error for empty path: {type(e).__name__}")

            self.test_results["error_handling_validation"] = error_handling_1

            # Test missing file handling
            load_result = stimulus_generator.load_stimulus_sequence(
                "nonexistent_file.json"
            )
            error_handling_2 = not load_result.success
            self.test_results["error_handling_missing_file"] = error_handling_2
            print(f"Missing file handling: {'PASS' if error_handling_2 else 'FAIL'}")

            # Test invalid experiment ID
            experiment_workflow = self.services["experiment_workflow"]
            status_result = experiment_workflow.get_experiment_status("invalid_id")
            error_handling_3 = not status_result.success
            self.test_results["error_handling_invalid_id"] = error_handling_3
            print(f"Invalid ID handling: {'PASS' if error_handling_3 else 'FAIL'}")

        except Exception as e:
            print(f"Error handling test failed: {e}")
            self.test_results["error_handling_validation"] = False
            self.test_results["error_handling_missing_file"] = False
            self.test_results["error_handling_invalid_id"] = False

        print()

    def _test_frame_synchronization(self) -> None:
        """Test frame synchronization functionality."""
        print("4. TESTING FRAME SYNCHRONIZATION")
        print("-" * 40)

        try:
            frame_synchronizer = self.services["frame_synchronizer"]

            # Create mock camera and stimulus frames
            camera_frames = self._create_mock_camera_frames(10)
            stimulus_frames = self._create_mock_stimulus_frames(10)

            # Test frame synchronization
            sync_result = frame_synchronizer.synchronize_frames(
                camera_frames, stimulus_frames
            )

            sync_successful = sync_result.success and sync_result.data
            self.test_results["sync_frame_synchronization"] = sync_successful
            print(f"Frame synchronization: {'PASS' if sync_successful else 'FAIL'}")

            # Test photodiode signal detection
            photodiode_result = frame_synchronizer.detect_photodiode_signals(
                camera_frames
            )

            photodiode_detection = photodiode_result.success and photodiode_result.data
            self.test_results["sync_photodiode_detection"] = photodiode_detection
            print(f"Photodiode detection: {'PASS' if photodiode_detection else 'FAIL'}")

            # Test sync quality calculation
            if sync_successful:
                quality_result = frame_synchronizer.calculate_sync_quality(
                    sync_result.data
                )

                quality_calculated = quality_result.success and quality_result.data
                self.test_results["sync_quality_calculation"] = quality_calculated
                print(
                    f"Sync quality calculation: {'PASS' if quality_calculated else 'FAIL'}"
                )
            else:
                self.test_results["sync_quality_calculation"] = False
                print("Sync quality calculation: SKIP (sync failed)")

        except Exception as e:
            print(f"Frame synchronization test failed: {e}")
            self.test_results["sync_frame_synchronization"] = False
            self.test_results["sync_photodiode_detection"] = False
            self.test_results["sync_quality_calculation"] = False

        print()

    def _test_analysis_pipeline(self) -> None:
        """Test data analysis pipeline."""
        print("5. TESTING ANALYSIS PIPELINE")
        print("-" * 40)

        try:
            data_analyzer = self.services["data_analyzer"]

            # Create analysis parameters
            analysis_params = self._create_test_analysis_parameters()

            # Test complete analysis
            analysis_result = data_analyzer.analyze_experiment_data(analysis_params)

            analysis_successful = analysis_result.success and analysis_result.data
            self.test_results["analysis_complete"] = analysis_successful
            print(f"Complete analysis: {'PASS' if analysis_successful else 'FAIL'}")

            # Test response map generation
            camera_frames = self._create_mock_camera_frames(5)
            stimulus_frames = self._create_mock_stimulus_frames(5)

            response_result = data_analyzer.generate_response_maps(
                camera_frames, stimulus_frames, analysis_params
            )

            response_maps_generated = response_result.success and response_result.data
            self.test_results["analysis_response_maps"] = response_maps_generated
            print(
                f"Response map generation: {'PASS' if response_maps_generated else 'FAIL'}"
            )

            # Test statistics calculation
            mock_response_data = {"amplitude": [0.1, 0.2, 0.3], "phase": [0, 90, 180]}
            stats_result = data_analyzer.calculate_statistics(
                mock_response_data, analysis_params
            )

            stats_calculated = stats_result.success and stats_result.data
            self.test_results["analysis_statistics"] = stats_calculated
            print(f"Statistics calculation: {'PASS' if stats_calculated else 'FAIL'}")

            # Test results export
            if analysis_successful:
                export_result = data_analyzer.export_results(
                    analysis_result.data, "json"
                )

                export_successful = export_result.success and export_result.data
                self.test_results["analysis_export"] = export_successful
                print(f"Results export: {'PASS' if export_successful else 'FAIL'}")
            else:
                self.test_results["analysis_export"] = False
                print("Results export: SKIP (analysis failed)")

        except Exception as e:
            print(f"Analysis pipeline test failed: {e}")
            self.test_results["analysis_complete"] = False
            self.test_results["analysis_response_maps"] = False
            self.test_results["analysis_statistics"] = False
            self.test_results["analysis_export"] = False

        print()

    def _print_test_summary(self) -> None:
        """Print comprehensive test summary."""
        print("6. TEST SUMMARY")
        print("-" * 40)

        passed_tests = sum(self.test_results.values())
        total_tests = len(self.test_results)
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print(f"Tests passed: {passed_tests}/{total_tests} ({pass_rate:.1f}%)")
        print()

        # Group results by category
        categories = {
            "Service Factory": [
                "service_factory_registration",
                "service_factory_creation",
                "service_factory_singleton",
            ],
            "Workflow": [
                "workflow_experiment_creation",
                "workflow_setup_validation",
                "workflow_stimulus_generation",
                "workflow_acquisition_init",
                "workflow_phase_transition",
                "workflow_validation",
            ],
            "Error Handling": [
                "error_handling_validation",
                "error_handling_missing_file",
                "error_handling_invalid_id",
            ],
            "Synchronization": [
                "sync_frame_synchronization",
                "sync_photodiode_detection",
                "sync_quality_calculation",
            ],
            "Analysis": [
                "analysis_complete",
                "analysis_response_maps",
                "analysis_statistics",
                "analysis_export",
            ],
        }

        for category, tests in categories.items():
            category_passed = sum(self.test_results.get(test, False) for test in tests)
            category_total = len(tests)
            print(f"{category}: {category_passed}/{category_total} passed")

        print()
        if passed_tests == total_tests:
            print(
                "🎉 ALL TESTS PASSED! ISI workflow refactor is complete and functional."
            )
        else:
            print("❌ Some tests failed. Please review the implementation.")

    # Helper methods for creating test data

    def _create_test_setup_parameters(self) -> SetupParameters:
        """Create test setup parameters."""
        return SetupParameters(
            monitor_size=(24.0, 18.0),
            monitor_resolution=(1920, 1080),
            monitor_distance=15.0,
            monitor_elevation=0.0,
            monitor_rotation=0.0,
            mouse_eye_height=3.0,
            mouse_visual_field_vertical=140.0,
            mouse_visual_field_horizontal=180.0,
            table_width=60.0,
            table_depth=40.0,
            table_height=75.0,
            photodiode_location="top_right",
            photodiode_size=100,
        )

    def _create_test_stimulus_parameters(self) -> StimulusParameters:
        """Create test stimulus parameters."""
        return StimulusParameters(
            stimulus_type="drifting_bar",
            duration=2.0,
            fps=30,
            contrast=1.0,
            orientation=0.0,
            width=10.0,
            speed=5.0,
            spatial_frequency=None,
            temporal_frequency=None,
            phase_shift=0.0,
            square_wave=False,
            retinotopy_mode=None,
            cycles=None,
            background_color=(128, 128, 128),
            bar_color=(255, 255, 255),
            photodiode_flash=True,
        )

    def _create_test_acquisition_parameters(
        self, output_dir: str
    ) -> AcquisitionParameters:
        """Create test acquisition parameters."""
        return AcquisitionParameters(
            camera_device_id=0,
            camera_resolution=(640, 480),
            camera_fps=30,
            camera_exposure=16.67,
            camera_gain=None,
            stimulus_monitor_id=1,
            main_monitor_id=0,
            fullscreen_stimulus=True,
            sync_tolerance_ms=16.67,
            buffer_size=100,
            save_camera_frames=True,
            save_stimulus_frames=True,
            output_directory=output_dir,
            compression_quality=95,
        )

    def _create_test_analysis_parameters(self) -> AnalysisParameters:
        """Create test analysis parameters."""
        return AnalysisParameters(
            experiment_id="test_experiment",
            analysis_type="response_mapping",
            camera_data_path="/tmp/camera_data",
            stimulus_data_path="/tmp/stimulus_data",
            spatial_filter_sigma=2.0,
            temporal_filter_cutoff=0.1,
            baseline_frames=30,
            response_window_ms=(100.0, 500.0),
            generate_response_maps=True,
            generate_statistics=True,
            generate_plots=True,
            output_format="png",
        )

    def _create_mock_camera_frames(self, count: int) -> List:
        """Create mock camera frames for testing."""
        from ..src.interfaces.experiment_interfaces import CameraFrame
        import numpy as np

        frames = []
        for i in range(count):
            frame_data = np.random.randint(
                0, 255, (480, 640, 3), dtype=np.uint8
            ).tobytes()
            frame = CameraFrame(
                frame_number=i,
                timestamp=i * 0.033,  # 30 FPS
                camera_timestamp=i * 0.033,  # Same as timestamp for testing
                frame_data=frame_data,
                synchronized_stimulus_frame=None,
                sync_confidence=0.0,
                metadata={"test": True},
            )
            frames.append(frame)
        return frames

    def _create_mock_stimulus_frames(self, count: int) -> List:
        """Create mock stimulus frames for testing."""
        from ..src.interfaces.experiment_interfaces import StimulusFrame

        frames = []
        for i in range(count):
            frame = StimulusFrame(
                frame_number=i,
                timestamp=i * 0.033,  # 30 FPS
                frame_data=b"mock_frame_data",
                photodiode_state=i % 10 == 0,  # Flash every 10th frame
                metadata={"test": True},
            )
            frames.append(frame)
        return frames


def main():
    """Run the integration test suite."""
    try:
        test_suite = ISIIntegrationTest()
        success = test_suite.run_complete_integration_test()

        return 0 if success else 1

    except Exception as e:
        print(f"\n💥 Integration test suite failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
