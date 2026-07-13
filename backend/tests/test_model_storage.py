from pathlib import Path

from app.ml.train_model import get_model_path


def test_model_path_can_use_persistent_data_directory(monkeypatch, tmp_path):
    expected = tmp_path / "risk_model.pkl"
    monkeypatch.setenv("SHADOWAI_MODEL_PATH", str(expected))
    assert get_model_path() == expected


def test_default_model_path_is_inside_application():
    path = get_model_path({})
    assert path.name == "risk_model.pkl"
    assert "models" in path.parts
