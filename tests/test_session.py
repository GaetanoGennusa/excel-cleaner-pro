"""Exercise the real Streamlit script through AppTest, without a browser."""
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from excel_cleaner.profile import profile_data

APP = Path(__file__).resolve().parents[1] / "app.py"


def button(app, label):
    return next(widget for widget in app.button if widget.label == label)


def loaded_app():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    source = pd.DataFrame({"code": ["001", "002"], "name": [" Ada ", "Demo"]}, dtype=object)
    # AppTest cannot upload files; seed the state after the independently tested reader.
    app.session_state["original"] = source
    app.session_state["profile"] = profile_data(source)
    app.run()
    assert not app.exception
    return app


def test_initial_screen_is_local_and_waits_for_upload():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    assert app.title[0].value == "Excel Cleaner Pro"
    assert "original" not in app.session_state


def test_default_apply_trim_undo_reset_and_clear():
    app = loaded_app()
    assert not any(checkbox.value for checkbox in app.checkbox)
    button(app, "Applica e mostra anteprima").click().run()
    assert not app.exception
    assert app.session_state["result"].modified_rows == 0
    assert any("Nessuna trasformazione selezionata" in message.value for message in app.info)
    trim = next(widget for widget in app.checkbox if widget.label.startswith("Rimuovi spazi"))
    trim.check()
    button(app, "Applica e mostra anteprima").click().run()
    assert not app.exception
    assert app.session_state["result"].data.loc[0, "name"] == "Ada"
    assert app.session_state["original"].loc[0, "name"] == " Ada "
    button(app, "Annulla ultima applicazione").click().run()
    assert not app.exception
    assert app.session_state["result"].data.loc[0, "name"] == " Ada "
    assert button(app, "Annulla ultima applicazione").disabled
    button(app, "Ripristina dati originali").click().run()
    assert not app.exception
    assert "result" not in app.session_state
    button(app, "Cancella dati della sessione").click().run()
    assert not app.exception
    assert "original" not in app.session_state


def test_export_buttons_prepare_real_files_in_memory():
    app = loaded_app()
    button(app, "Applica e mostra anteprima").click().run()
    button(app, "Prepara esportazioni").click().run()
    assert not app.exception
    assert app.session_state["report"].startswith(b"PK")
    assert app.session_state["csv_export"].startswith(b"\xef\xbb\xbf")


def test_explicit_date_widget_commits_format_and_export():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    source = pd.DataFrame({"code": ["001", "002"], "date": ["01/02/2025", "31/02/2025"]})
    app.session_state["original"] = source
    app.session_state["profile"] = profile_data(source)
    app.run()
    next(widget for widget in app.selectbox if widget.label == "date · data").select("%d/%m/%Y")
    button(app, "Applica e mostra anteprima").click().run()
    assert not app.exception
    result = app.session_state["result"]
    assert result.config["date_columns"] == {"date": "%d/%m/%Y"}
    assert result.data["date"].tolist() == ["2025-02-01", "31/02/2025"]
    assert result.modified_rows == 1
    button(app, "Prepara esportazioni").click().run()
    from io import BytesIO
    from openpyxl import load_workbook
    workbook = load_workbook(BytesIO(app.session_state["report"]))
    assert workbook["Cleaned_Data"]["B2"].value == "2025-02-01"
    assert app.session_state["original"].loc[0, "date"] == "01/02/2025"
    workbook.close()


def test_confirmation_alone_keeps_duplicates_and_explains_original_export():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    source = pd.DataFrame({"code": ["001", "001"], "name": [" Demo ", " Demo "]})
    app.session_state["original"] = source
    app.session_state["profile"] = profile_data(source)
    app.run()
    next(widget for widget in app.checkbox if widget.label.startswith("Confermo la rimozione")).check()
    button(app, "Applica e mostra anteprima").click().run()
    assert not app.exception
    result = app.session_state["result"]
    pd.testing.assert_frame_equal(result.data, source)
    assert result.removed_rows == 0
    assert result.modified_rows == 0
    assert any("Nessuna trasformazione selezionata" in message.value for message in app.info)
