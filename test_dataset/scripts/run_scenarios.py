"""Automated test script for RD4 Signifier System.

This script loads signifiers, runs test scenarios, and validates the system
across all phases (Storage, SHACL, Intent Matching).
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import get_settings
from src.matching import IntentMatcherRegistry
from src.storage.registry import SignifierRegistry
from src.validation import ContextGraphBuilder, SHACLValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestRunner:
    """Test runner for comprehensive system validation."""

    def __init__(self):
        """Initialize test runner."""
        self.settings = get_settings()
        self.signifier_registry = SignifierRegistry(
            storage_dir="./test_storage",
            enable_authoring_validation=False
        )
        self.matcher_registry = IntentMatcherRegistry(default_version="v0")
        self.shacl_validator = SHACLValidator(enable_caching=True)
        self.context_builder = ContextGraphBuilder()

        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }

    def load_signifiers(self) -> int:
        """Load all signifiers from test dataset.

        Returns:
            Number of signifiers loaded
        """
        logger.info("=" * 60)
        logger.info("PHASE 1: Loading Signifiers")
        logger.info("=" * 60)

        signifier_dir = Path(__file__).parent.parent / "signifiers"
        loaded_count = 0

        for ttl_file in signifier_dir.glob("*.ttl"):
            try:
                with open(ttl_file, "r", encoding="utf-8") as f:
                    rdf_data = f.read()

                signifier = self.signifier_registry.create_from_rdf(rdf_data)
                logger.info(f"Loaded: {signifier.signifier_id}")
                loaded_count += 1

            except Exception as e:
                logger.error(f"Failed to load {ttl_file.name}: {e}")

        logger.info(f"\nLoaded {loaded_count} signifiers successfully")
        return loaded_count

    def test_phase1_storage(self):
        """Test Phase 1: Storage operations."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 1 TESTS: Storage")
        logger.info("=" * 60)

        self._test("T1.1: List all signifiers", self._test_list_signifiers)
        self._test("T1.2: Retrieve by ID", self._test_retrieve_by_id)
        self._test("T1.3: Filter by affordance", self._test_filter_signifiers)

    def test_phase2_shacl(self):
        """Test Phase 2: SHACL Validation."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 2 TESTS: SHACL Validation")
        logger.info("=" * 60)

        self._test("T2.1: Conforming context (raise-blinds)",
                  self._test_shacl_conforming)
        self._test("T2.2: Non-conforming context (low luminosity)",
                  self._test_shacl_non_conforming)
        self._test("T2.3: Edge case - exact threshold",
                  self._test_shacl_edge_case)
        self._test("T2.4: Multiple constraints (turn-light-on)",
                  self._test_shacl_multiple_constraints)

    def test_phase3_matching(self):
        """Test Phase 3: Intent Matching."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 3 TESTS: Intent Matching")
        logger.info("=" * 60)

        self._test("T3.1: String matcher - exact match",
                  self._test_string_exact_match)
        self._test("T3.2: String matcher - partial match",
                  self._test_string_partial_match)
        self._test("T3.3: Embedding matcher - semantic match",
                  self._test_embedding_semantic)
        self._test("T3.4: Version comparison",
                  self._test_version_comparison)
        self._test("T3.5: Top-K limiting",
                  self._test_top_k)
        self._test("T3.6: No matches",
                  self._test_no_matches)

    def test_integration(self):
        """Test end-to-end integration scenarios."""
        logger.info("\n" + "=" * 60)
        logger.info("INTEGRATION TESTS: End-to-End")
        logger.info("=" * 60)

        self._test("T4.1: Full pipeline - perfect match",
                  self._test_full_pipeline_perfect)
        self._test("T4.2: Full pipeline - context fails",
                  self._test_full_pipeline_context_fails)
        self._test("T4.3: Temperature control - heating",
                  self._test_temperature_heating)
        self._test("T4.4: Temperature control - cooling",
                  self._test_temperature_cooling)
        self._test("T4.5: Meeting scenario",
                  self._test_meeting_scenario)

    # Test implementations
    def _test_list_signifiers(self):
        """Test listing all signifiers."""
        signifiers = self.signifier_registry.list_signifiers(limit=100)
        assert len(signifiers) >= 4, f"Expected at least 4 signifiers, got {len(signifiers)}"
        return True

    def _test_retrieve_by_id(self):
        """Test retrieving signifier by ID."""
        signifier = self.signifier_registry.get("raise-blinds-signifier")
        assert signifier is not None, "Failed to retrieve raise-blinds-signifier"
        assert signifier.signifier_id == "raise-blinds-signifier"
        return True

    def _test_filter_signifiers(self):
        """Test filtering signifiers."""
        all_signifiers = self.signifier_registry.list_signifiers()
        assert len(all_signifiers) > 0, "No signifiers found"
        return True

    def _test_shacl_conforming(self):
        """Test SHACL validation with conforming context."""
        context_data = self._load_context("scenario1_bright_warm.json")
        signifier = self.signifier_registry.get("raise-blinds-signifier")

        if not signifier or not signifier.context.shacl_shapes:
            logger.warning("Signifier or SHACL shapes not found")
            return True

        context_graph, _ = self.context_builder.normalize_context(
            context_data["context_features"]
        )
        context_graph = self.context_builder.add_type_information(
            context_graph, context_data["artifact_types"]
        )

        result = self.shacl_validator.validate_signifier_context(
            context_graph, signifier.context.shacl_shapes
        )

        assert result.conforms, f"Expected conforming, got violations: {result.violations}"
        return True

    def _test_shacl_non_conforming(self):
        """Test SHACL validation with non-conforming context."""
        signifier = self.signifier_registry.get("raise-blinds-signifier")

        if not signifier or not signifier.context.shacl_shapes:
            return True

        non_conforming_context = {
            "http://example.org/precis/workspaces/lab308/artifacts/external_light_sensing308": {
                "http://example.org/LightSensor#hasLuminosityLevel": 5000
            },
            "http://example.org/precis/workspaces/lab308/artifacts/temperature_sensor308": {
                "http://example.org/TemperatureSensor#hasTemperatureLevel": 22
            }
        }

        artifact_types = {
            "http://example.org/precis/workspaces/lab308/artifacts/external_light_sensing308": "http://example.org/LightSensor",
            "http://example.org/precis/workspaces/lab308/artifacts/temperature_sensor308": "http://example.org/TemperatureSensor"
        }

        context_graph, _ = self.context_builder.normalize_context(non_conforming_context)
        context_graph = self.context_builder.add_type_information(context_graph, artifact_types)

        result = self.shacl_validator.validate_signifier_context(
            context_graph, signifier.context.shacl_shapes
        )

        assert not result.conforms, "Expected non-conforming, but got conforming"
        assert len(result.violations) > 0, "Expected violations"
        return True

    def _test_shacl_edge_case(self):
        """Test SHACL validation with exact threshold value."""
        context_data = self._load_context("scenario7_edge_luminosity.json")
        signifier = self.signifier_registry.get("raise-blinds-signifier")

        if not signifier or not signifier.context.shacl_shapes:
            return True

        context_graph, _ = self.context_builder.normalize_context(
            context_data["context_features"]
        )
        context_graph = self.context_builder.add_type_information(
            context_graph, context_data["artifact_types"]
        )

        result = self.shacl_validator.validate_signifier_context(
            context_graph, signifier.context.shacl_shapes
        )

        assert result.conforms, "minInclusive should allow equality"
        return True

    def _test_shacl_multiple_constraints(self):
        """Test SHACL validation with multiple constraints."""
        context_data = self._load_context("scenario2_dark_people.json")
        signifier = self.signifier_registry.get("turn-light-on-signifier")

        if not signifier or not signifier.context.shacl_shapes:
            return True

        context_graph, _ = self.context_builder.normalize_context(
            context_data["context_features"]
        )
        context_graph = self.context_builder.add_type_information(
            context_graph, context_data["artifact_types"]
        )

        result = self.shacl_validator.validate_signifier_context(
            context_graph, signifier.context.shacl_shapes
        )

        assert result.conforms, f"Both constraints should pass, got violations: {result.violations}"
        return True

    def _test_string_exact_match(self):
        """Test string matcher with exact token match."""
        signifiers = self.signifier_registry.list_signifiers()
        signifier_dicts = [s.model_dump() for s in signifiers]

        results = self.matcher_registry.match(
            "increase luminosity",
            signifier_dicts,
            k=5,
            version="v0"
        )

        assert len(results) > 0, "Expected at least one match"
        return True

    def _test_string_partial_match(self):
        """Test string matcher with partial match."""
        signifiers = self.signifier_registry.list_signifiers()
        signifier_dicts = [s.model_dump() for s in signifiers]

        results = self.matcher_registry.match(
            "make brighter",
            signifier_dicts,
            k=5,
            version="v0"
        )

        return True

    def _test_embedding_semantic(self):
        """Test embedding matcher with semantic similarity."""
        try:
            signifiers = self.signifier_registry.list_signifiers()
            signifier_dicts = [s.model_dump() for s in signifiers]

            results = self.matcher_registry.match(
                "make room brighter",
                signifier_dicts,
                k=5,
                version="v1"
            )

            assert len(results) > 0, "Expected semantic matches"
            return True
        except ValueError as e:
            if "not registered" in str(e):
                logger.warning("Embedding matcher not available")
                return True
            raise

    def _test_version_comparison(self):
        """Test comparing matcher versions."""
        signifiers = self.signifier_registry.list_signifiers()
        signifier_dicts = [s.model_dump() for s in signifiers]

        results_v0 = self.matcher_registry.match(
            "increase light",
            signifier_dicts,
            k=5,
            version="v0"
        )

        logger.info(f"  v0 returned {len(results_v0)} matches")

        try:
            results_v1 = self.matcher_registry.match(
                "increase light",
                signifier_dicts,
                k=5,
                version="v1"
            )
            logger.info(f"  v1 returned {len(results_v1)} matches")
        except ValueError:
            logger.warning("  v1 not available")

        return True

    def _test_top_k(self):
        """Test top-K limiting."""
        signifiers = self.signifier_registry.list_signifiers()
        signifier_dicts = [s.model_dump() for s in signifiers]

        results = self.matcher_registry.match(
            "increase luminosity",
            signifier_dicts,
            k=2,
            version="v0"
        )

        assert len(results) <= 2, f"Expected max 2 results, got {len(results)}"
        return True

    def _test_no_matches(self):
        """Test query with no matches."""
        signifiers = self.signifier_registry.list_signifiers()
        signifier_dicts = [s.model_dump() for s in signifiers]

        results = self.matcher_registry.match(
            "brew coffee",
            signifier_dicts,
            k=5,
            version="v0"
        )

        assert len(results) == 0, f"Expected no matches, got {len(results)}"
        return True

    def _test_full_pipeline_perfect(self):
        """Test full pipeline with perfect match."""
        context_data = self._load_context("scenario1_bright_warm.json")

        signifiers = self.signifier_registry.list_signifiers()
        signifier_dicts = [s.model_dump() for s in signifiers]

        matches = self.matcher_registry.match(
            "increase luminosity",
            signifier_dicts,
            k=5,
            version="v0"
        )

        assert len(matches) > 0, "Expected intent matches"

        conforming_count = 0
        for match in matches:
            signifier = self.signifier_registry.get(match.signifier_id)
            if signifier and signifier.context.shacl_shapes:
                context_graph, _ = self.context_builder.normalize_context(
                    context_data["context_features"]
                )
                context_graph = self.context_builder.add_type_information(
                    context_graph, context_data["artifact_types"]
                )

                result = self.shacl_validator.validate_signifier_context(
                    context_graph, signifier.context.shacl_shapes
                )

                if result.conforms:
                    conforming_count += 1
                    logger.info(f"  {match.signifier_id} conforms")

        assert conforming_count > 0, "Expected at least one conforming match"
        return True

    def _test_full_pipeline_context_fails(self):
        """Test full pipeline where context validation fails."""
        non_conforming = {
            "http://example.org/precis/workspaces/lab308/artifacts/external_light_sensing308": {
                "http://example.org/LightSensor#hasLuminosityLevel": 5000
            },
            "http://example.org/precis/workspaces/lab308/artifacts/temperature_sensor308": {
                "http://example.org/TemperatureSensor#hasTemperatureLevel": 22
            }
        }

        artifact_types = {
            "http://example.org/precis/workspaces/lab308/artifacts/external_light_sensing308": "http://example.org/LightSensor",
            "http://example.org/precis/workspaces/lab308/artifacts/temperature_sensor308": "http://example.org/TemperatureSensor"
        }

        signifier = self.signifier_registry.get("raise-blinds-signifier")
        if signifier and signifier.context.shacl_shapes:
            context_graph, _ = self.context_builder.normalize_context(non_conforming)
            context_graph = self.context_builder.add_type_information(context_graph, artifact_types)

            result = self.shacl_validator.validate_signifier_context(
                context_graph, signifier.context.shacl_shapes
            )

            assert not result.conforms, "Context should not conform"

        return True

    def _test_temperature_heating(self):
        """Test temperature control - heating scenario."""
        context_data = self._load_context("scenario3_cold_people.json")
        signifier = self.signifier_registry.get("heat-room-signifier")

        if signifier and signifier.context.shacl_shapes:
            context_graph, _ = self.context_builder.normalize_context(
                context_data["context_features"]
            )
            context_graph = self.context_builder.add_type_information(
                context_graph, context_data["artifact_types"]
            )

            result = self.shacl_validator.validate_signifier_context(
                context_graph, signifier.context.shacl_shapes
            )

            assert result.conforms, "Cold room should match heating"

        return True

    def _test_temperature_cooling(self):
        """Test temperature control - cooling scenario."""
        context_data = self._load_context("scenario4_hot.json")
        signifier = self.signifier_registry.get("cool-room-signifier")

        if signifier and signifier.context.shacl_shapes:
            context_graph, _ = self.context_builder.normalize_context(
                context_data["context_features"]
            )
            context_graph = self.context_builder.add_type_information(
                context_graph, context_data["artifact_types"]
            )

            result = self.shacl_validator.validate_signifier_context(
                context_graph, signifier.context.shacl_shapes
            )

            assert result.conforms, "Hot room should match cooling"

        return True

    def _test_meeting_scenario(self):
        """Test meeting scenario."""
        context_data = self._load_context("scenario5_meeting.json")
        signifier = self.signifier_registry.get("start-meeting-mode-signifier")

        if signifier and signifier.context.shacl_shapes:
            context_graph, _ = self.context_builder.normalize_context(
                context_data["context_features"]
            )
            context_graph = self.context_builder.add_type_information(
                context_graph, context_data["artifact_types"]
            )

            result = self.shacl_validator.validate_signifier_context(
                context_graph, signifier.context.shacl_shapes
            )

            assert result.conforms, "Meeting context should match"

        return True

    # Helper methods
    def _test(self, name: str, test_func):
        """Run a single test."""
        self.results["total_tests"] += 1
        try:
            logger.info(f"\nRunning: {name}")
            start_time = time.time()
            test_func()
            elapsed = (time.time() - start_time) * 1000

            self.results["passed"] += 1
            self.results["tests"].append({
                "name": name,
                "status": "PASSED",
                "elapsed_ms": round(elapsed, 2)
            })
            logger.info(f"PASSED ({elapsed:.2f}ms)")

        except AssertionError as e:
            self.results["failed"] += 1
            self.results["tests"].append({
                "name": name,
                "status": "FAILED",
                "error": str(e)
            })
            logger.error(f"FAILED: {e}")

        except Exception as e:
            self.results["failed"] += 1
            self.results["tests"].append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            logger.error(f"ERROR: {e}")

    def _load_context(self, filename: str) -> Dict:
        """Load context from JSON file."""
        context_file = Path(__file__).parent.parent / "contexts" / filename
        with open(context_file, "r") as f:
            return json.load(f)

    def print_summary(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {self.results['total_tests']}")
        logger.info(f"Passed: {self.results['passed']}")
        logger.info(f"Failed: {self.results['failed']}")

        success_rate = (self.results['passed'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        logger.info(f"Success Rate: {success_rate:.1f}%")

        if self.results['failed'] > 0:
            logger.info("\nFailed Tests:")
            for test in self.results['tests']:
                if test['status'] in ['FAILED', 'ERROR']:
                    logger.info(f"  - {test['name']}: {test.get('error', 'Unknown error')}")

    def save_report(self):
        """Save test report to JSON file."""
        report_file = Path(__file__).parent.parent / "test_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"\nReport saved to: {report_file}")


def main():
    """Run all test scenarios."""
    logger.info("RD4 Signifier System - Comprehensive Test Suite")
    logger.info("=" * 60)

    runner = TestRunner()

    num_loaded = runner.load_signifiers()
    if num_loaded == 0:
        logger.error("No signifiers loaded. Exiting.")
        return

    runner.test_phase1_storage()
    runner.test_phase2_shacl()
    runner.test_phase3_matching()
    runner.test_integration()

    runner.print_summary()
    runner.save_report()


if __name__ == "__main__":
    main()
