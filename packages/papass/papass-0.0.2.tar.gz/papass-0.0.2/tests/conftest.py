from hypothesis import settings

base = settings(print_blob=True)

settings.register_profile("dev", parent=base, max_examples=10)
settings.register_profile("ci", parent=base, max_examples=1000)
