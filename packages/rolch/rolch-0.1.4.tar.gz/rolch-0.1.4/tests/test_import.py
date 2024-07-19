def test_import():
    try:
        import rolch

        failed = False
    except Exception as e:
        failed = True

    assert ~failed, f"Import failed with Exception {e}."
