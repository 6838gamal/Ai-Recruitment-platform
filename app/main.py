*** Begin Patch
*** Update File: app/main.py
@@
-from fastapi.templating import Jinja2Templates
+from fastapi.templating import Jinja2Templates
+from app.utils.enhanced_templates import EnhancedJinja2Templates
@@
-templates = Jinja2Templates(
-    directory="app/templates"
-)
+# Use the enhanced templates globally so all modules benefit from the
+# compatibility wrapper without changing individual modules.
+templates = EnhancedJinja2Templates(directory="app/templates")
*** End Patch
