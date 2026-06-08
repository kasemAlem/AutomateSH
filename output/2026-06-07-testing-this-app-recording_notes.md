# Recording Notes for: **One Property Test That Replaces 50 Unit Tests**

## Code to Record
```
import * as fc from 'fast-check';
// Invariant: processUser should never throw, even for insane inputs
test('processUser handles any possible input', () => {
  fc.assert(
    fc.property(fc.anything(), (input) => {
      // This single line generates NaN, null, undefined, arrays — everything
      const result = processUser(input);
      return typeof result === 'string' || result === null;
    })
  );
});
```

## Original Script (with visual cues)
Stop testing what you *expect* to happen—start testing what you *don’t* expect. You ship a feature, your suite passes, then a null object crashes production for 40% of users. Switch to property-based testing with `fast-check`: define your function’s invariants, and the framework generates thousands of random edge cases—`NaN`, `undefined`, empty arrays—your manual tests miss. Here's one property test that replaces 50 hand-written unit tests. Follow for more testing shortcuts that prevent P0 incidents.
