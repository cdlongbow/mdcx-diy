pyuic6 mdcx/views/MDCx.ui -o mdcx/views/MDCx.py
pyuic6 mdcx/views/posterCutTool.ui -o mdcx/views/posterCutTool.py

# Fix PyQt6 6.11+ enum compatibility (flat enums -> nested enums)
python scripts/fix_qt_enums.py mdcx/views/MDCx.py mdcx/views/posterCutTool.py
