from papass.random.system import SystemRng


def test_system():
    rng = SystemRng()

    for _ in range(100):
        assert 0 <= rng.randbelow(5) < 5
