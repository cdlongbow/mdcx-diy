REP_WORD = {
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&apos;": "'",
    "&quot;": '"',
    "&lsquo;": "\u300c",
    "&rsquo;": "\u300d",
    "&hellip;": "\u2026",
    "<br/>": "",
    "\u30fb": "\u00b7",
    "\u201c": "\u300c",
    "\u201d": "\u300d",
    "...": "\u2026",
    "\xa0": "",
    "\u3000": "",
    "\u2800": "",
}

ESCAPE_WORD = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&apos;",
    '"': "&quot;",
}

XML_TEXT_FIELDS = [
    "title",
    "originaltitle",
    "number",
    "outline",
    "originalplot",
    "series",
    "studio",
    "publisher",
]


def normalize_xml_text(raw: str) -> str:
    for key, value in REP_WORD.items():
        raw = raw.replace(key, value)
    return raw


def escape_xml_text(raw: str) -> str:
    raw = normalize_xml_text(raw)
    for key, value in ESCAPE_WORD.items():
        raw = raw.replace(key, value)
    return raw


def build_cdata(raw: str) -> str:
    normalized = normalize_xml_text(raw)
    return "<![CDATA[" + normalized.replace("]]>", "]]]]><![CDATA[>") + "]]>"
