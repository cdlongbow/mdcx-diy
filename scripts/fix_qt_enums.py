"""
Post-process pyuic6 output to fix PyQt6 6.11+ enum compatibility.

PyQt6 6.11 moved flat enums (Qt.AlignCenter) to nested enums (Qt.AlignmentFlag.AlignCenter).
Old pyuic6 generates flat enums that don't work with PyQt6 6.11+.
This script fixes them after pyuic6 compilation.

Usage:
    python fix_qt_enums.py <file.py> [file2.py ...]
"""

import re
import sys
from pathlib import Path

# Migration rules: (flat_enum_name, category)
# Grouped by category. Order within each group matters (longer names first).
MIGRATIONS = {
    # (category_prefix_for_Qt, category_prefix_for_QFrame, replacements)
    'Qt': [
        # ContextMenuPolicy
        ('ContextMenuPolicy', 'ActionsContextMenu'),
        ('ContextMenuPolicy', 'DefaultContextMenu'),
        ('ContextMenuPolicy', 'NoContextMenu'),
        ('ContextMenuPolicy', 'PreventContextMenu'),
        ('ContextMenuPolicy', 'CustomContextMenu'),
        # CursorShape
        ('CursorShape', 'ArrowCursor'),
        ('CursorShape', 'UpArrowCursor'),
        ('CursorShape', 'CrossCursor'),
        ('CursorShape', 'WaitCursor'),
        ('CursorShape', 'IBeamCursor'),
        ('CursorShape', 'SizeVerCursor'),
        ('CursorShape', 'SizeHorCursor'),
        ('CursorShape', 'SizeAllCursor'),
        ('CursorShape', 'PointingHandCursor'),
        ('CursorShape', 'WhatsThisCursor'),
        ('CursorShape', 'BusyCursor'),
        ('CursorShape', 'ForbiddenCursor'),
        ('CursorShape', 'SplitVCursor'),
        ('CursorShape', 'SplitHCursor'),
        ('CursorShape', 'OpenHandCursor'),
        ('CursorShape', 'ClosedHandCursor'),
        ('CursorShape', 'SizeBDiagCursor'),
        ('CursorShape', 'SizeFDiagCursor'),
        ('CursorShape', 'BlankCursor'),
        # ScrollBarPolicy
        ('ScrollBarPolicy', 'ScrollBarAsNeeded'),
        ('ScrollBarPolicy', 'ScrollBarAlwaysOff'),
        ('ScrollBarPolicy', 'ScrollBarAlwaysOn'),
        # TextFormat
        ('TextFormat', 'AutoText'),
        ('TextFormat', 'PlainText'),
        ('TextFormat', 'RichText'),
        ('TextFormat', 'MarkdownText'),
        # AlignmentFlag - longer names first
        ('AlignmentFlag', 'AlignTrailing'),
        ('AlignmentFlag', 'AlignLeading'),
        ('AlignmentFlag', 'AlignJustify'),
        ('AlignmentFlag', 'AlignHCenter'),
        ('AlignmentFlag', 'AlignVCenter'),
        ('AlignmentFlag', 'AlignCenter'),
        ('AlignmentFlag', 'AlignRight'),
        ('AlignmentFlag', 'AlignLeft'),
        ('AlignmentFlag', 'AlignTop'),
        ('AlignmentFlag', 'AlignBottom'),
        ('AlignmentFlag', 'AlignBaseline'),
        ('AlignmentFlag', 'AlignAuto'),
        # TextInteractionFlag - longer names first
        ('TextInteractionFlag', 'TextEditorInteraction'),
        ('TextInteractionFlag', 'TextBrowserInteraction'),
        ('TextInteractionFlag', 'LinksAccessibleByKeyboard'),
        ('TextInteractionFlag', 'LinksAccessibleByMouse'),
        ('TextInteractionFlag', 'TextSelectableByKeyboard'),
        ('TextInteractionFlag', 'TextSelectableByMouse'),
        ('TextInteractionFlag', 'TextEditable'),
        ('TextInteractionFlag', 'NoTextInteraction'),
        # LayoutDirection
        ('LayoutDirection', 'LayoutDirectionAuto'),
        ('LayoutDirection', 'LayoutDirectionUndefined'),
        ('LayoutDirection', 'LeftToRight'),
        ('LayoutDirection', 'RightToLeft'),
        # Orientation
        ('Orientation', 'Horizontal'),
        ('Orientation', 'Vertical'),
        # FocusPolicy
        ('FocusPolicy', 'WheelFocus'),
        ('FocusPolicy', 'StrongFocus'),
        ('FocusPolicy', 'ClickFocus'),
        ('FocusPolicy', 'TabFocus'),
        ('FocusPolicy', 'NoFocus'),
        # TextElideMode
        ('TextElideMode', 'ElideMiddle'),
        ('TextElideMode', 'ElideRight'),
        ('TextElideMode', 'ElideLeft'),
        ('TextElideMode', 'ElideNone'),
        # DropAction
        ('DropAction', 'CopyAction'),
        ('DropAction', 'MoveAction'),
        ('DropAction', 'LinkAction'),
        ('DropAction', 'IgnoreAction'),
        # WindowState
        ('WindowState', 'WindowActive'),
        ('WindowState', 'WindowMinimized'),
        ('WindowState', 'WindowMaximized'),
        ('WindowState', 'WindowFullScreen'),
        ('WindowState', 'WindowClose'),
        ('WindowState', 'WindowShade'),
        ('WindowState', 'WindowNoState'),
        # AspectRatioMode
        ('AspectRatioMode', 'KeepAspectRatioByExpanding'),
        ('AspectRatioMode', 'KeepAspectRatio'),
        ('AspectRatioMode', 'IgnoreAspectRatio'),
    ],
    'QFrame': [
        # QFrame.Shape
        ('Shape', 'StyledPanel'),
        ('Shape', 'GroupBoxPanel'),
        ('Shape', 'StyledLine'),
        ('Shape', 'WinPanel'),
        ('Shape', 'Panel'),
        ('Shape', 'HLine'),
        ('Shape', 'VLine'),
        ('Shape', 'Box'),
        ('Shape', 'NoFrame'),
        # QFrame.Shadow
        ('Shadow', 'Sunken'),
        ('Shadow', 'Raised'),
        ('Shadow', 'Plain'),
    ],
}


def build_patterns():
    """Build regex patterns that avoid matching already-migrated code."""
    patterns = []
    for cls_name, migrations in MIGRATIONS.items():
        for category, enum_name in migrations:
            # Match: Qt.EnumName or QtCore.Qt.EnumName or QFrame.Shape etc
            # But NOT Qt.Category.EnumName (already migrated)
            # Use negative lookahead (?!\.) to ensure enum name isn't followed by dot
            # Use negative lookbehind to avoid matching category name as enum
            old = rf'{cls_name}\.{enum_name}(?!\.)'
            new = f'{cls_name}.{category}.{enum_name}'
            patterns.append((old, new))
    return patterns


def fix_enums_in_file(filepath: str) -> int:
    """Fix PyQt6 enum references in a file. Returns number of replacements."""
    path = Path(filepath)
    if not path.exists():
        print(f"  [SKIP] {filepath} not found")
        return 0

    content = path.read_text(encoding='utf-8')
    patterns = build_patterns()
    total = 0

    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            count = len(re.findall(pattern, content))
            content = new_content
            total += count
            print(f"  {count:4d} x  {pattern} -> {replacement}")

    if total > 0:
        path.write_text(content, encoding='utf-8')
    return total


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_qt_enums.py <file.py> [file2.py ...]")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        print(f"Processing: {filepath}")
        count = fix_enums_in_file(filepath)
        if count == 0:
            print("  No changes needed.")
        else:
            print(f"  Total: {count} replacements")
        print()


if __name__ == "__main__":
    main()
