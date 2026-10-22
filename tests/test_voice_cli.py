import unittest

from avcis.voice.speech_to_text import build_parser


class SpeechToTextCliTests(unittest.TestCase):
    def test_default_duration_is_five_seconds(self):
        arguments = build_parser().parse_args([])
        self.assertEqual(arguments.duration, 5.0)

    def test_custom_duration_is_supported(self):
        arguments = build_parser().parse_args(["--duration", "8"])
        self.assertEqual(arguments.duration, 8.0)

    def test_list_devices_flag_is_supported(self):
        arguments = build_parser().parse_args(["--list-devices"])
        self.assertTrue(arguments.list_devices)


if __name__ == "__main__":
    unittest.main()