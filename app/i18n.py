"""German / English toggle for the app's own interface text.

Only phrases written by us are translated (titles, headings, captions, labels, buttons). Text that comes from
the data or the kb files (finding evidence, measure descriptions, ticket quotes, assistant answers) stays as stored:
translating it would change a source. Numbers are never touched: no phrase below contains a digit
(test_app.I18nTests checks this), so a translated page shows exactly the figures of the English page.
"""
from __future__ import annotations

import functools

import streamlit as st

KEY = "lang_de"

# English phrase -> German. Longest phrases are applied first, so a short phrase never splits a longer one.
DE: dict[str, str] = {
    # navigation and sidebar
    "Overall picture": "Gesamtbild",
    "Findings": "Befunde",
    "Measures package": "Massnahmenpaket",
    "Package": "Paket",
    "Needs a human": "Braucht einen Menschen",
    "Ask the data": "Frag die Daten",
    "Next year": "Nächstes Jahr",
    "Reload data": "Daten neu laden",
    "Numbers:": "Zahlen:",
    "Sample data ALTYCA, sprintd Basel": "Beispieldaten ALTYCA, sprintd Basel",
    # factor switch
    "What the jury might recalculate": "Was die Jury nachrechnen könnte",
    "Low factors": "Tiefe Faktoren",
    "Mid factors": "Mittlere Faktoren",
    "High factors": "Hohe Faktoren",
    # overview
    "Baseline year": "Basisjahr",
    "every number from": "jede Zahl aus",
    "Location-based CO2 per year": "Standortbasiertes CO2 pro Jahr",
    " factors</div>": " Faktoren</div>",
    "on low and high factors": "bei tiefen und hohen Faktoren",
    "Energy (": "Energie (",
    "Range ": "Spanne ",
    "Same on every factor set": "Gleich bei jedem Faktorensatz",
    "How this number was calculated": "So wurde diese Zahl berechnet",
    "accounts for": "verursacht",
    "of the CO2, and": "des CO2, und",
    "is the largest resource at": "ist die grösste Ressource mit",
    "The chart shows": "Die Grafik zeigt",
    "By department": "Nach Abteilung",
    "How departments are split": "So werden Abteilungen aufgeteilt",
    "By tool": "Nach Tool",
    "By country": "Nach Land",
    "Cost per month": "Kosten pro Monat",
    "Table view: all resources": "Tabelle: alle Ressourcen",
    "Table view: countries": "Tabelle: Länder",
    "Table view: per source": "Tabelle: pro Quelle",
    "Table view: every finding": "Tabelle: alle Befunde",
    "Table view": "Tabelle",
    "Cost": "Kosten",
    # findings
    "Ranked by addressable CO2 (location-based, mid factors)": "Sortiert nach adressierbarem CO2 (standortbasiert, mittlere Faktoren)",
    "How to read this page": "So liest man diese Seite",
    "Largest:": "Grösster:",
    "CO2 a year": "CO2 pro Jahr",
    "Needs human review": "Braucht menschliche Prüfung",
    "Candidate": "Kandidat",
    "Protected: keep": "Geschützt: behalten",
    "Idle or unused": "Ungenutzt",
    "Energy, mid": "Energie, mittel",
    "CO2, location-based mid": "CO2, standortbasiert mittel",
    "Baseline cost of the resource:": "Basiskosten der Ressource:",
    "Resource ": "Ressource ",
    "Evidence:": "Beleg:",
    "Protection rule:": "Schutzregel:",
    "How this was calculated": "So wurde das berechnet",
    "The other ": "Die übrigen ",
    " findings": " Befunde",
    # package
    "Case targets per year:": "Zielvorgaben pro Jahr:",
    "(location-based)": "(standortbasiert)",
    "at most": "höchstens",
    "person-days": "Personentage",
    "rows from": "Zeilen aus",
    "targets met": "Ziele erreicht",
    "targets missed": "Ziele verfehlt",
    "All ": "Alle ",
    " of ": " von ",
    "CO2 reduction": "CO2-Reduktion",
    "Cost reduction": "Kostenreduktion",
    "Budget": "Budget",
    "target ": "Ziel ",
    "PASS": "ERFÜLLT",
    "MISS": "VERFEHLT",
    "CLOSE": "KNAPP",
    "How CO2 was calculated": "So wurde CO2 berechnet",
    "How cost was calculated": "So wurden die Kosten berechnet",
    "How the budget was calculated": "So wurde das Budget berechnet",
    "Energy saved, mid factor only:": "Eingesparte Energie, nur mittlerer Faktor:",
    "(the measure file stores one energy column)": "(die Massnahmendatei speichert eine Energiespalte)",
    "Chosen package in": "Gewähltes Paket in",
    "Unticking a row shows the trade-off against that package.": "Abwählen einer Zeile zeigt den Zielkonflikt zu diesem Paket.",
    "Sensitivity: if paused hours count at idle power": "Sensitivität: pausierte Stunden mit Leerlaufleistung",
    "Tick measures on or off": "Massnahmen an- oder abwählen",
    "Reset to the chosen package": "Auf das gewählte Paket zurücksetzen",
    "Protection rule, change and the calculation on each row": "Schutzregel, Änderung und Berechnung pro Zeile",
    # needs a human
    "Text that tries to steer an AI": "Text, der eine KI steuern will",
    "Looks idle, must not be switched off": "Wirkt ungenutzt, darf nicht abgeschaltet werden",
    "Sources that disagree": "Quellen, die sich widersprechen",
    "One-off costs: real, but never a recurring saving": "Einmalkosten: echt, aber nie eine wiederkehrende Einsparung",
    "Notice dates": "Kündigungstermine",
    "Also respect": "Ebenfalls beachten",
    # ask the data
    "Offline · answers come from": "Offline · Antworten stammen aus",
    "text inside the data is data, never an instruction": "Text in den Daten ist Daten, nie eine Anweisung",
    "Ask about cost, seats, servers, protection rules …": "Frag nach Kosten, Lizenzen, Servern, Schutzregeln …",
    "Numbers behind this answer": "Zahlen hinter dieser Antwort",
    "Refused.": "Abgelehnt.",
    "Calculating …": "Berechne …",
    # next year
    "Nothing on this page is added to the package.": "Nichts auf dieser Seite wird zum Paket addiert.",
    "From ": "Aus ",
    "Our own AI use": "Unsere eigene KI-Nutzung",
    "Our AI use during the sprint": "Unsere KI-Nutzung im Sprint",
    "location-based CO2, mid factors": "standortbasiertes CO2, mittlere Faktoren",
    "Counted so far:": "Bisher gezählt:",
    "Not counted yet:": "Noch nicht gezählt:",
    "Method and tokens (V6 note)": "Methode und Tokens (V6-Notiz)",
    "Production platform, baseline months": "Produktionsplattform, Basismonate",
    "Carbon-aware job shift": "Klimabewusste Job-Verschiebung",
    "Source:": "Quelle:",
    "· cost −": "· Kosten −",
    "` from `pipeline": "` aus `pipeline",
}
# Generic words that also occur inside data text. They are translated only in our own labels, titles and the
# HTML we generate, never in markdown or captions, which can carry evidence or descriptions from the files.
LABEL_ONLY = {" of ", "All ", "Cost", "From ", "Range ", "target ", "Resource ", "The other ", " findings", "Source:",
              "Budget", "Candidate", "Package", "Findings", "Next year", "Energy (", " factors</div>", "PASS", "MISS",
              "CLOSE", "Table view", "Baseline year"}
_ORDER = sorted(DE, key=len, reverse=True)
_ORDER_SAFE = [p_ for p_ in _ORDER if p_ not in LABEL_ONLY]


def is_de() -> bool:
    try:
        return bool(st.session_state.get(KEY, False))
    except Exception:  # no session (plain import in a test)
        return False


def tr(text, *, label: bool = True):
    """Translate our own phrases when German is on. label=False (markdown, captions) skips generic words."""
    if not isinstance(text, str) or not is_de():
        return text
    out = text
    for en in (_ORDER if label else _ORDER_SAFE):
        if en in out:
            out = out.replace(en, DE[en])
    return out


# Our own labels and titles: full table. Body text that may quote data: safe table only.
_LABEL_FNS = ["title", "header", "subheader", "popover", "expander", "button", "toggle", "metric", "chat_input",
              "spinner", "html"]
_BODY_FNS = ["markdown", "caption", "info", "warning", "error", "badge"]


def install(module=st) -> None:
    """Wrap the text functions once per process. In English mode the wrappers change nothing."""
    if getattr(module, "_i18n_installed", False):
        return

    def make(fn, label: bool):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            if args:
                args = (tr(args[0], label=label),) + args[1:]
            if "label" in kwargs:
                kwargs["label"] = tr(kwargs["label"])
            return fn(*args, **kwargs)
        return wrapped

    for name in _LABEL_FNS + _BODY_FNS:
        orig = getattr(module, name, None)
        if orig is not None:
            setattr(module, name, make(orig, name in _LABEL_FNS))
    tabs = module.tabs
    module.tabs = functools.wraps(tabs)(lambda labels, *a, **k: tabs([tr(x) for x in labels], *a, **k))
    seg = module.segmented_control

    @functools.wraps(seg)
    def seg_wrapped(label, options, *a, **k):
        k.setdefault("format_func", tr)  # options keep their English values; only the shown text changes
        return seg(tr(label), options, *a, **k)
    module.segmented_control = seg_wrapped
    module._i18n_installed = True
