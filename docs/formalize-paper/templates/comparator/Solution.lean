/-
Copyright (c) 2026 <Author>. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Author>
-/
-- One import per file proving a headline result of formalization.yaml.
import <Lib>.<Paper>.<Result>

/-! # Comparator solution module

The solution side of the [comparator](https://github.com/leanprover/comparator) setup in
`comparator/`: this module imports the project files proving the headline results listed in
`formalization.yaml`, so its environment contains, at the exact names stated (with `sorry`) in
the `comparator/Challenge_*.lean` files, the headline theorems of the paper (see
`comparator/README.md`). -/
