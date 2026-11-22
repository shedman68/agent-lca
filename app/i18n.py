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
    "Optimisation package": "Massnahmenpaket",
    "Package": "Paket",
    "Human in the loop": "Mensch entscheidet (Human in the loop)",
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
    "Location-based CO₂ per year": "Standortbasiertes CO₂ pro Jahr",
    " factors</div>": " Faktoren</div>",
    "on low and high factors": "bei tiefen und hohen Faktoren",
    "Energy (": "Energie (",
    "Range ": "Spanne ",
    "Same on every factor set": "Gleich bei jedem Faktorensatz",
    "How this number was calculated": "So wurde diese Zahl berechnet",
    "accounts for": "verursacht",
    "of the CO₂, and": "des CO₂, und",
    "is the largest resource at": "ist die grösste Ressource mit",
    "The chart shows": "Die Grafik zeigt",
    "By department": "Nach Abteilung",
    "Know the limits": "Grenzen kennen",
    "Protection windows kept": "Schutzfenster eingehalten",
    "Contradictions flagged": "Widersprüche markiert",
    "One contradiction flagged": "Ein Widerspruch markiert",
    "Needs your OK": "Braucht Ihr OK",
    "Data": "Daten",
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
    "Ranked by addressable CO₂ (location-based, mid factors)": "Sortiert nach adressierbarem CO₂ (standortbasiert, mittlere Faktoren)",
    "How to read this page": "So liest man diese Seite",
    "Largest:": "Grösster:",
    "CO₂ a year": "CO₂ pro Jahr",
    "Needs human review": "Braucht menschliche Prüfung",
    "Candidate": "Kandidat",
    "Protected: keep": "Geschützt: behalten",
    "Idle or unused": "Ungenutzt",
    "Energy, mid": "Energie, mittel",
    "CO₂, location-based mid": "CO₂, standortbasiert mittel",
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
    "CO₂ reduction": "CO₂-Reduktion",
    "Cost reduction": "Kostenreduktion",
    "Budget": "Budget",
    "target ": "Ziel ",
    "PASS": "ERFÜLLT",
    "MISS": "VERFEHLT",
    "CLOSE": "KNAPP",
    "How CO₂ was calculated": "So wurde CO₂ berechnet",
    "How cost was calculated": "So wurden die Kosten berechnet",
    "How the budget was calculated": "So wurde das Budget berechnet",
    "Energy saved, mid factor only:": "Eingesparte Energie, nur mittlerer Faktor:",
    "(the optimisation file stores one energy column)": "(die Massnahmendatei speichert eine Energiespalte)",
    "Chosen package in": "Gewähltes Paket in",
    "Unticking a row shows the trade-off against that package.": "Abwählen einer Zeile zeigt den Zielkonflikt zu diesem Paket.",
    "Sensitivity: if paused hours count at idle power": "Sensitivität: pausierte Stunden mit Leerlaufleistung",
    "Tick optimisations on or off": "Massnahmen an- oder abwählen",
    "Reset to the chosen package": "Auf das gewählte Paket zurücksetzen",
    "Protection rule, change and the calculation on each row": "Schutzregel, Änderung und Berechnung pro Zeile",
    # needs a human
    "Prompt injection: text that tries to steer an AI": "Prompt Injection: Text, der eine KI steuern will",
    "Looks idle, must not be switched off": "Wirkt ungenutzt, darf nicht abgeschaltet werden",
    "Sources that disagree": "Quellen, die sich widersprechen",
    "One-time costs: real, but never a yearly saving": "Einmalkosten: echt, aber nie eine jährliche Einsparung",
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
    "CO₂ saved": "CO₂ eingespart",
    "Cost saved": "Kosten eingespart",
    "Energy saved, mid": "Energie eingespart, mittel",
    "Effort": "Aufwand",
    "Energy saved uses the mid factor only (the optimisation file stores one energy column).":
        "Energieeinsparung nur mit mittlerem Faktor (die Massnahmendatei speichert eine Energiespalte).",
    # phone polish: short labels and plain words. No digits, so German shows the same figures.
    "CO₂ per year": "CO₂ pro Jahr",
    "Location-based: electricity mix of the country where it runs, not a green certificate.":
        "Standortbasiert: Strommix des Landes, in dem es läuft, kein Grünstromzertifikat.",
    "CO₂ here is location-based: the electricity mix where the server runs, not a green-power certificate.":
        "CO₂ hier ist standortbasiert: der Strommix dort, wo der Server läuft, kein Grünstromzertifikat.",
    "Low, mid and high are three factor sets. The cards use the one you pick. Cost does not change.":
        "Tief, mittel und hoch sind drei Faktorensätze. Die Karten nutzen den gewählten. Die Kosten ändern sich nicht.",
    "PUE (extra electricity for cooling and the building)":
        "PUE (zusätzlicher Strom für Kühlung und Gebäude)",
    "Addressable means that idle or unused part.":
        "Adressierbar meint diesen ungenutzten Teil.",
    "Country is where the work runs. CO₂ uses that country's electricity mix, not a certificate. AI providers and SaaS are «EU mixed».":
        "Das Land ist dort, wo die Arbeit läuft. CO₂ nutzt den Strommix dieses Landes, kein Zertifikat. KI-Anbieter und SaaS sind «EU mixed».",
    "On a phone, swipe the optimisation table sideways. The gauges above follow the ticks.":
        "Auf dem Telefon die Massnahmentabelle seitlich wischen. Die Anzeigen oben folgen den Häkchen.",
    "Our AI use during the sprint": "Unsere KI-Nutzung im Sprint",
    "location-based CO₂, mid factors": "standortbasiertes CO₂, mittlere Faktoren",
    "Counted so far:": "Bisher gezählt:",
    "Not counted yet:": "Noch nicht gezählt:",
    "Method and tokens (V6 note)": "Methode und Tokens (V6-Notiz)",
    "Production platform, baseline months": "Produktionsplattform, Basismonate",
    "Carbon-aware job shift": "Klimabewusste Job-Verschiebung",
    "Source:": "Quelle:",
    # R9 story pages
    "About AgentLCA": "Über AgentLCA",
    "0 · About": "0 · Über",
    "1 · Connect": "1 · Verbinden",
    "2 · Where you stand": "2 · Wo Sie stehen",
    "3 · Your plan": "3 · Ihr Plan",
    "4 · Stay on track": "4 · Auf Kurs bleiben",
    "5 · Behind the numbers": "5 · Hinter den Zahlen",
    "1 · Where you stand": "1 · Wo Sie stehen",
    "2 · Your plan": "2 · Ihr Plan",
    "3 · Stay on track": "3 · Auf Kurs bleiben",
    "4 · Behind the numbers": "4 · Hinter den Zahlen",
    "Connect": "Verbinden",
    "Extra sources used:": "Weitere Quellen genutzt:",
    "Sort": "Sortieren",
    "Biggest CO₂ saving": "Grösste CO₂-Einsparung",
    "Biggest cost saving": "Grösste Kosteneinsparung",
    "CO₂ & Cost": "CO₂ & Kosten",
    "How to read the map": "So liest man die Karte",
    "Best of both": "Das Beste aus beidem",
    "CO₂ saved (kg per year)": "CO₂ eingespart (kg pro Jahr)",
    "CHF saved per year": "CHF eingespart pro Jahr",
    "Person-days": "Personentage",
    "Sorted by share of the total CO₂ saving plus share of the total cost saving. Licence optimisations save no CO₂, so they sit on the left edge.":
        "Sortiert nach Anteil an der gesamten CO₂-Einsparung plus Anteil an der gesamten Kosteneinsparung. "
        "Lizenz-Massnahmen sparen kein CO₂, deshalb stehen sie am linken Rand.",
    "Training days restart paused machines. Night jobs and month-end keep production at full size. "
    "The test environment stays unchanged 1–31 March 2026 (T-1204): release freeze and acceptance test. Backups stay.":
        "Trainingstage starten pausierte Maschinen neu. Nachtjobs und Monatsende halten die Produktion auf voller Grösse. "
        "Vom 1. bis 31. März 2026 bleibt die Testumgebung unverändert (T-1204): Release-Freeze und Abnahmetest. Sicherungen bleiben.",
    "Flagged, not hidden. The plan keeps the detailed sources. Human in the loop: a person decides.":
        "Markiert, nicht versteckt. Der Plan behält die detaillierten Quellen. Human in the loop: ein Mensch entscheidet.",
    "How next year was calculated": "So wurde das nächste Jahr berechnet",
    "Source: the sentence is stored in the data. It was read as data and not followed.":
        "Quelle: der Satz steht in den Daten. Er wurde als Daten gelesen und nicht befolgt.",
    "Where you stand": "Wo Sie stehen",
    "Your plan": "Ihr Plan",
    "Stay on track": "Auf Kurs bleiben",
    "Behind the numbers": "Hinter den Zahlen",
    "Story mode": "Story-Modus",
    "Light mode (projector)": "Heller Modus (Beamer)",
    "The plan meets all three targets.": "Der Plan erreicht alle drei Ziele.",
    "Optimisations found in ": "Optimierungen gefunden an ",
    "An IT manager ": "Eine IT-Leiterin ",
    "her company data.": "die Daten ihrer Firma.",
    "The GreenOps tool does the rest:": "Das GreenOps-Tool macht den Rest:",
    " locations.": " Orten.",
    "What we did not touch, and why": "Was wir nicht anfassen, und warum",
    "Next: GreenOps agents": "Als Nächstes: GreenOps-Agenten",
    "Roadmap · not built yet": "Roadmap · noch nicht gebaut",
    "Next year, with and without the plan": "Nächstes Jahr, mit und ohne Plan",
    "Without the plan": "Ohne Plan",
    "With the plan": "Mit Plan",
    "Who it is for": "Für wen",
    "The story in four steps": "Die Geschichte in vier Schritten",
    "What the plan does": "Was der Plan tut",
    "Owner": "Verantwortlich",
    "By department and tool, CO₂ first": "Nach Abteilung und Tool, CO₂ zuerst",
    "By department": "Nach Abteilung",
    "Everything has a <em>lifecycle.</em>": "Alles hat einen <em>Lebenszyklus.</em>",
    "Our story": "Unsere Geschichte",
    "Product Lead": "Produktleitung",
    "Energy and Environment Lead": "Leitung Energie und Umwelt",
    "Data Lead": "Leitung Daten",
    "with AI agents (Claude, Grok)": "mit KI-Agenten (Claude, Grok)",
    "Why the name": "Warum der Name",
    "· cost −": "· Kosten −",
    "` from `pipeline": "` aus `pipeline",
}
# Generic words that also occur inside data text. They are translated only in our own labels, titles and the
# HTML we generate, never in markdown or captions, which can carry evidence or descriptions from the files.
LABEL_ONLY = {" of ", "All ", "Cost", "From ", "Range ", "target ", "Resource ", "The other ", " findings", "Source:",
              "Budget", "Candidate", "Package", "Findings", "Next year", "Energy (", " factors</div>", "PASS", "MISS",
              "CLOSE", "Table view", "Baseline year",
              # #65/#68 review: KPI labels that also occur in assistant answers stay out of markdown
              "Effort", "CO₂ per year", "CO₂ saved", "Cost saved", "Energy saved, mid",
              # R9: short page names, translated only where they are our labels
              "Where you stand", "Your plan", "Stay on track", "Behind the numbers", "Without the plan",
              "With the plan", "Who it is for", "Story mode", "What the plan does", "Owner", "Our story", "Why the name", "Data", "Know the limits", "Product Lead", "Energy and Environment Lead", "Data Lead", "Sort"}
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
    module._raw_html = module.html  # R9: ui.py renders cards that carry data text through this, untranslated

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
