"""Visual helpers; dataset values are never interpolated into HTML."""
from collections.abc import Mapping
from html import escape
from pathlib import Path

import streamlit as st

THEME = Path(__file__).with_name("theme.css")
STEPS = [("Carica", "Carica"), ("Esamina", "Esamina"), ("Scegli le regole", "Regole"),
         ("Verifica", "Verifica"), ("Esporta", "Esporta")]
CHECK_LABELS = {"row_accounting": "Numero di righe coerente", "column_count_preserved": "Tutte le colonne conservate",
                "unique_headers": "Intestazioni univoche", "deletion_authorized": "Eliminazioni autorizzate",
                "source_order_preserved": "Ordine della sorgente conservato",
                "missing_values_preserved": "Valori mancanti conservati"}


def apply_design() -> None:
    """Load the local stylesheet; it has no external URLs."""
    st.html(f"<style>{THEME.read_text(encoding='utf-8')}</style>")


def brand() -> None:
    st.html('''<div class="ecp-brand"><span class="ecp-brand-mark" aria-hidden="true">EC</span>
      <div><strong>Excel Cleaner Pro</strong><small>Il tuo spazio di lavoro locale</small></div></div>''')


def hero_badge() -> None:
    st.html('<span class="ecp-eyebrow"><span class="ecp-live" aria-hidden="true"></span>'
            'Locale · Verificabile · Senza telemetria</span>')


def hero_lede() -> None:
    st.html('<p class="ecp-lede"><strong>Pulisci i tuoi file.</strong> Tieni ogni modifica sotto controllo.</p>')


def hero_chips() -> None:
    st.html('<ul class="ecp-chips" aria-label="Caratteristiche"><li>Excel e CSV</li>'
            '<li>Elaborazione sul tuo computer</li><li>Originali sempre conservati</li></ul>')


def hero_demo() -> None:
    """Decorative card with fixed synthetic examples, not uploaded data."""
    rows = [("␣Ada␣␣Test␣", "Ada Test", ""), ("1.234,56", "1234.56", ""), ("BRUNO DEMO", "Bruno Demo", ""),
            ("001", "001 · protetto", " ecp-keep")]
    body = "".join(f'<div class="ecp-demo-row{extra}"><span class="ecp-before">{escape(before)}</span>'
                   f'<span class="ecp-arrow" aria-hidden="true">→</span><span class="ecp-after">{escape(after)}</span></div>'
                   for before, after, extra in rows)
    st.html('<div class="ecp-demo" aria-hidden="true"><div class="ecp-demo-head"><span>Esempio di pulizia</span>'
            '<span><span class="ecp-live"></span>Log attivo</span></div>' + body +
            '<div class="ecp-demo-foot"><b>4 regole</b> · ogni modifica registrata con riga, prima e dopo</div></div>')


def workflow(active: int) -> str:
    """Return a status indicator, never a simulated navigation control."""
    items = []
    for position, (label, short) in enumerate(STEPS):
        status = "active" if position == active else "done" if position < active else ""
        if position == active - 1:
            status += " latest"
        current = ' aria-current="step"' if position == active else ""
        marker = "✓" if position < active else str(position + 1)
        state = " (completata)" if position < active else " (in corso)" if position == active else ""
        items.append(f'<li class="{status.strip()}"{current}><span class="ecp-step-dot" aria-hidden="true">{marker}</span>'
                     f'<span><span class="ecp-full">{label}</span><span class="ecp-short" aria-hidden="true">{short}</span>'
                     f'<span class="ecp-sr">Fase {position + 1}{state}</span></span></li>')
    return '<ol class="ecp-workflow" aria-label="Fasi di lavoro">' + "".join(items) + "</ol>"


def tag(label: str, after: bool = False) -> None:
    st.html(f'<span class="ecp-tag{" after" if after else ""}">{escape(label)}</span>')


def file_badge(kind: str) -> None:
    st.html(f'<span class="ecp-file {escape(kind.lower())}">{escape(kind.upper())}</span>')


def rule_count(config: Mapping) -> int:
    """Confirmation alone is not a selected transformation."""
    return (sum(bool(config.get(name)) for name in ["trim", "headers", "drop_duplicates"])
            + sum(len(config.get(name, {})) for name in ["case_columns", "number_columns", "date_columns"]))


def integrity_summary(checks: Mapping[str, bool]) -> None:
    if all(checks.values()):
        st.success("Controlli di integrità superati")
    else:
        st.error("Alcuni controlli di integrità non sono superati")
    chips = "".join(f'<li class="{"" if passed else "failed"}">{escape(CHECK_LABELS.get(key, key))}</li>'
                    for key, passed in checks.items())
    st.html(f'<ul class="ecp-checks" aria-label="Controlli effettuati">{chips}</ul>')
