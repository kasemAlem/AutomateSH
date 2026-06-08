# Recording Notes for: **One Failing Test That Saves Your Next Deployment**

## Code to Record
```
import unittest

def calculate_total(prices: list) -> float:
    # Bug: returns sum instead of total with tax
    return sum(prices)

class TestCheckout(unittest.TestCase):
    def test_calculate_total_with_tax(self):
        # Arrange: set up input prices
        prices = [10.00, 20.00, 5.00]
        # Act: call the function (the "magic" line that catches regressions)
        result = calculate_total(prices)
        # Assert: verify expected total including 8% tax
        self.assertAlmostEqual(result, 37.80, places=2)

if __name__ == "__main__":
    unittest.main()
```

## Original Script (with visual cues)
Write one test that fails, and you’ve already saved yourself from the next deployment disaster. You just spent twenty minutes clicking the same buttons, then broke the feature with your very next commit. Stop repeating manual regression — write a single unit test using Arrange-Act-Assert. Here’s the three lines: `arrange` the inputs, `act` on the function, `assert` the result. Follow for more automation shortcuts.
