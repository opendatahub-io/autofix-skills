"""Route admission policy checked with the Z3 solver."""

import z3


def route_is_admissible(max_tokens: int, budget: int) -> bool:
    """Return True if a request of max_tokens fits within the remaining budget."""
    tokens = z3.Int("tokens")
    solver = z3.Solver()
    solver.add(tokens == max_tokens, tokens >= 0, tokens <= budget)
    return solver.check() == z3.sat


if __name__ == "__main__":
    print(f"libz3 {z3.get_version_string()}")
