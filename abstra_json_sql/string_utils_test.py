from unittest import TestCase, main

from abstra_json_sql.string_utils import snake_case


class TestSnakeCaseUtils(TestCase):
    def test_snake_case(self):
        self.assertEqual(snake_case("Hello World"), "hello_world")
        self.assertEqual(snake_case("snake_case"), "snake_case")
        self.assertEqual(snake_case("Test123"), "test_123")
        self.assertEqual(snake_case("test with spaces"), "test_with_spaces")
        self.assertEqual(snake_case("UPPERCASE"), "uppercase")


if __name__ == "__main__":
    main()
