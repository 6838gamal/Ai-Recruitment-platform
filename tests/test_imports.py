def test_import_routes():
    import importlib
    importlib.import_module("app.modules.accounts.routes")
    importlib.import_module("app.modules.candidates.routes")
    importlib.import_module("app.modules.ats.routes")
    importlib.import_module("app.modules.resume_parser.routes")
    importlib.import_module("app.modules.settings.routes")
    importlib.import_module("app.modules.ai_matching.routes")
