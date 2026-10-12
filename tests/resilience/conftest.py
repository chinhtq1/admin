"""Attach-only to the emspoc stack; tests that stop/start services must call compose_stack.stop()/start(),
which refuse unless EMS_TEST_OWN_STACK=1 (Docker stack owner only)."""
