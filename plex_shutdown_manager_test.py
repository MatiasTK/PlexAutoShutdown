"""     Test file for plex_shutdown_manager.py """
import unittest
import subprocess
from unittest.mock import MagicMock, patch
from plex_shutdown_manager import (
    PlexShutdownManager,
    NO_ACTIVATION,
    ACTIVATED_SHUTDOWN,
    CANCELED_SHUTDOWN,
)

SHUTDOWN_DELAY = 3600


class PlexShutdownManagerTest(unittest.TestCase):
    """Test class for plex_shutdown_manager.py"""

    def setUp(self) -> None:
        self.patcher = patch("plex_shutdown_manager.toast")
        self.mock_toast = self.patcher.start()
        self.app_mock = MagicMock()

    def tearDown(self) -> None:
        self.patcher.stop()
        try:
            subprocess.run(["shutdown", "-a"], check=True)
        except subprocess.CalledProcessError:
            print("Shutdown was not canceled")

    def test_01_framework(self):
        """Test if the test framework is working"""
        self.assertEqual(1, 1)

    def test_02_activate_shutdown(self):
        """Test if the shutdown is activated"""
        psm = PlexShutdownManager(self.app_mock)
        psm.activate_shutdown(SHUTDOWN_DELAY)
        self.assertTrue(psm.shutdown_enabled)
        try:
            subprocess.run(["shutdown", "-a"], check=True)
        except subprocess.CalledProcessError:
            self.fail("Shutdown was not activated")
        assert self.mock_toast.call_count == 1

    def test_03_cancel_shutdown(self):
        """Test if the shutdown is canceled"""
        psm = PlexShutdownManager(self.app_mock)
        psm.activate_shutdown(SHUTDOWN_DELAY)
        try:
            psm.cancel_shutdown()
        except subprocess.CalledProcessError:
            self.fail("Shutdown was not canceled")
        assert self.mock_toast.call_count == 1

    def test_04_cancel_shutdown_without_activation(self):
        """Test cancel shutdown without activation"""
        psm = PlexShutdownManager(self.app_mock)
        self.assertFalse(psm.cancel_shutdown())
        assert self.mock_toast.call_count == 0

    def test_05_no_app(self):
        """Test plex_shutdown_manager with app being none"""
        psm = PlexShutdownManager(None)
        self.assertFalse(psm.check_if_transcoder_running())
        self.assertFalse(psm.check_if_are_active_sessions())
        self.assertFalse(psm.monitor_plex_and_shutdown())

    def test_06_transcoder_running_plex_not(self):
        """Test plex_shutdown_manager with transcoder running but not the plex"""
        psm = PlexShutdownManager(self.app_mock)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[""],
                returncode=1,
                stdout="Plex Transcoder.exe",
            )
            self.assertFalse(psm.check_if_transcoder_running())

    def test_07_plex_running_transcoder_not(self):
        """Test plex_shutdown_manager with plex running but not transcoder"""
        psm = PlexShutdownManager(self.app_mock)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[""],
                returncode=1,
                stdout="Plex Media Server.exe\n",
            )
            self.assertFalse(psm.check_if_transcoder_running())

    def test_08_plex_running_transcoder_running(self):
        """Test plex_shutdown_manager with plex and transcoder running"""
        psm = PlexShutdownManager(self.app_mock)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[""],
                returncode=1,
                stdout="Plex Media Server.exe\n Plex Transcoder.exe",
            )
            self.assertTrue(psm.check_if_transcoder_running())

    def test_09_no_active_sessions(self):
        """Test plex_shutdown_manager with no active sessions"""
        psm = PlexShutdownManager(self.app_mock)
        plex_mock = MagicMock()
        plex_mock.sessions.return_value = []
        self.app_mock.get_plex_instance.return_value = plex_mock

        self.assertFalse(psm.check_if_are_active_sessions())

    def test_10_active_sessions(self):
        """Test plex_shutdown_manager with active sessions"""
        psm = PlexShutdownManager(self.app_mock)

        plex_mock = MagicMock()
        plex_mock.sessions.return_value = ["test", "test2"]
        self.app_mock.get_plex_instance.return_value = plex_mock

        self.assertTrue(psm.check_if_are_active_sessions())

    def test_11_minute_to_seconds(self):
        """Test plex_shutdown_manager with minute to seconds conversion"""
        self.assertEqual(PlexShutdownManager(None).minutes_to_seconds(1), 60)

    def test_12_monitor_without_app_or_switch_disabled(self):
        """Test plex_shutdown_manager monitor with app shutdown switch disabled"""
        self.app_mock.get_shutdown_status.return_value = False
        psm = PlexShutdownManager(self.app_mock)
        self.assertEqual(psm.monitor_plex_and_shutdown(), NO_ACTIVATION)

    def test_13_monitor_not_idling(self):
        """Test plex_shutdown_manager monitor with app shutdown switch enabled and not idling"""
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=10
        ):
            self.assertEqual(psm.monitor_plex_and_shutdown(), NO_ACTIVATION)

    def test_14_monitor_transcoder_not_running(self):
        """Test plex_shutdown_manager monitor with app shutdown switch enabled and idling and transcoder running"""
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=70
        ), patch.object(psm, "check_if_transcoder_running", return_value=True):
            self.assertEqual(psm.monitor_plex_and_shutdown(), NO_ACTIVATION)

    def test_15_monitor_no_active_sessions(self):
        """Test plex_shutdown_manager monitor with app shutdown switch enabled and idling and an active session"""
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=70
        ), patch.object(
            psm, "check_if_transcoder_running", return_value=False
        ), patch.object(
            psm, "check_if_are_active_sessions", return_value=True
        ):
            self.assertEqual(psm.monitor_plex_and_shutdown(), NO_ACTIVATION)

    def test_16_monitor_shutdown_enabled(self):
        """Test plex_shutdown_manager monitor with app shutdown switch enabled and idling but no active sessions"""
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=70
        ), patch.object(
            psm, "check_if_transcoder_running", return_value=False
        ), patch.object(
            psm, "check_if_are_active_sessions", return_value=False
        ), patch.object(
            psm, "shutdown_enabled", True
        ):
            self.assertEqual(psm.monitor_plex_and_shutdown(), NO_ACTIVATION)

    def test_17_monitor_cancel_activation(self):
        """Test plex_shutdown_manager monitor with app shutdown switch enabled and shutdown activated but not idling"""
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=10
        ), patch.object(
            psm, "check_if_transcoder_running", return_value=False
        ), patch.object(
            psm, "check_if_are_active_sessions", return_value=False
        ), patch.object(
            psm, "shutdown_enabled", True
        ):
            self.assertEqual(psm.monitor_plex_and_shutdown(), CANCELED_SHUTDOWN)

    def test_18_monitor_activate_shutdown(self):
        """Test plex_shutdown_manager monitor with app shutdown switch enabled and shutdown not activated and idling"""
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=70
        ), patch.object(
            psm, "check_if_transcoder_running", return_value=False
        ), patch.object(
            psm, "check_if_are_active_sessions", return_value=False
        ), patch.object(
            psm, "shutdown_enabled", False
        ):
            self.assertEqual(psm.monitor_plex_and_shutdown(), ACTIVATED_SHUTDOWN)

    def test_19_shutdown_enabled_now_not_idling(self):
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=1
        ), patch.object(psm, "shutdown_enabled", True):
            self.assertEqual(psm.monitor_plex_and_shutdown(), CANCELED_SHUTDOWN)

    def test_20_shutdown_enabled_new_session(self):
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=120
        ), patch.object(psm, "shutdown_enabled", True), patch.object(
            psm, "check_if_are_active_sessions", return_value=True
        ):
            self.assertEqual(psm.monitor_plex_and_shutdown(), CANCELED_SHUTDOWN)

    def test_21_shutdown_enabled_still_idling_no_new_session(self):
        psm = PlexShutdownManager(self.app_mock)
        with patch.object(psm, "minutes_to_seconds", return_value=60), patch(
            "plex_shutdown_manager.get_idle_duration", return_value=120
        ), patch.object(psm, "shutdown_enabled", True), patch.object(
            psm, "check_if_are_active_sessions", return_value=False
        ):
            self.assertEqual(psm.monitor_plex_and_shutdown(), NO_ACTIVATION)


if __name__ == "__main__":
    unittest.main()
