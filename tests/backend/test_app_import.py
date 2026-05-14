def test_fastapi_app_importable() -> None:
    from main import app

    assert app.title
