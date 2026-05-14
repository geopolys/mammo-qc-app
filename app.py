import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "11itCZA6RkbPY3jBSC2MZyDc4qb2k5g_gn1B0djm4o48"

def connect_to_gsheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

st.set_page_config(page_title="Weekly Mammography QC", layout="wide")

st.title("Πρωτόκολλο Εβδομαδιαίου Ποιοτικού Ελέγχου Ψηφιακής Μαστογραφίας")

centres = [
    "Κέντρο Μαστογραφίας Λευκωσίας - Κ.Υ. Αγλαντζιάς",
    "Κέντρο Μαστογραφίας Λεμεσού - Κ.Υ. Λινόπετρας",
    "Κέντρο Μαστογραφίας Λάρνακας - Ιατρικό Κέντρο Μακένζυ",
    "Κέντρο Μαστογραφίας Αμμοχώστου - Κ.Υ. Αμμοχώστου",
    "Κέντρο Μαστογραφίας Γεροσκήπου - Ιατρικό Κέντρο Γεροσκήπου"
]

with st.form("weekly_qc_form"):

    st.subheader("Στοιχεία Ελέγχου")

    qc_date = st.date_input("Ημερομηνία", value=date.today())
    centre = st.selectbox("Κέντρο / Νοσοκομείο", centres)
    radiographer = st.text_input("Ακτινογράφος")

    st.divider()

    st.subheader("Detector Flat Field Calibration")

    detector_ffc = st.selectbox(
        "Εκτελέστηκε η διαδικασία επιτυχώς;",
        ["ΝΑΙ", "ΟΧΙ"]
    )

    st.divider()

    st.subheader("Artifact Evaluation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Rh")
        rh_kv = st.number_input("Rh kV", min_value=0.0, step=0.1)
        rh_mas = st.number_input("Rh mAs", min_value=0.0, step=0.1)
        rh_result = st.selectbox("Rh Έλεγχος επιτυχής;", ["ΝΑΙ", "ΟΧΙ"])

    with col2:
        st.markdown("### Ag")
        ag_kv = st.number_input("Ag kV", min_value=0.0, step=0.1)
        ag_mas = st.number_input("Ag mAs", min_value=0.0, step=0.1)
        ag_result = st.selectbox("Ag Έλεγχος επιτυχής;", ["ΝΑΙ", "ΟΧΙ"])

    with col3:
        st.markdown("### Al")
        al_kv = st.number_input("Al kV", min_value=0.0, step=0.1)
        al_mas = st.number_input("Al mAs", min_value=0.0, step=0.1)
        al_result = st.selectbox("Al Έλεγχος επιτυχής;", ["ΝΑΙ", "ΟΧΙ"])

    st.divider()

    st.subheader("Image Quality - ACR Phantom")

    col2d, coldbt = st.columns(2)

    with col2d:
        st.markdown("### Image Modality: 2D")
        kv_2d = st.number_input("2D kV", min_value=0.0, step=0.1)
        mas_2d = st.number_input("2D mAs", min_value=0.0, step=0.1)
        agd_2d = st.number_input("2D AGD", min_value=0.0, step=0.01)

        fibers_2d = st.number_input("2D Fibers score", min_value=0.0, step=0.5)
        specs_2d = st.number_input("2D Specs group score", min_value=0.0, step=0.5)
        mass_2d = st.number_input("2D Mass score", min_value=0.0, step=0.5)

        if fibers_2d < 5 or specs_2d < 4 or mass_2d < 4:
            st.error("2D Image Quality: FAIL")
        else:
            st.success("2D Image Quality: PASS")

    with coldbt:
        st.markdown("### Image Modality: DBT")
        kv_dbt = st.number_input("DBT kV", min_value=0.0, step=0.1)
        mas_dbt = st.number_input("DBT mAs", min_value=0.0, step=0.1)
        agd_dbt = st.number_input("DBT AGD", min_value=0.0, step=0.01)

        fibers_dbt = st.number_input("DBT Fibers score", min_value=0.0, step=0.5)
        specs_dbt = st.number_input("DBT Specs group score", min_value=0.0, step=0.5)
        mass_dbt = st.number_input("DBT Mass score", min_value=0.0, step=0.5)

        if fibers_dbt < 4 or specs_dbt < 4 or mass_dbt < 4:
            st.error("DBT Image Quality: FAIL")
        else:
            st.success("DBT Image Quality: PASS")

    st.info("Όρια: 2D Fibers ≥ 5, Specs ≥ 4, Mass ≥ 4 | DBT Fibers ≥ 4, Specs ≥ 4, Mass ≥ 4")

    st.divider()

    st.subheader("Signal-To-Noise Ratio")

    snr_2d = st.number_input("2D SNR", min_value=0.0, step=0.1)

    st.info("Όριο: SNR ≥ 40")

    if snr_2d < 40:
        st.error("SNR: FAIL")
    else:
        st.success("SNR: PASS")

    st.divider()

    comments = st.text_area("Παρατηρήσεις")

    submitted = st.form_submit_button("Υποβολή Εβδομαδιαίου QC")

if submitted:

    result_2d = "PASS"
    result_dbt = "PASS"
    snr_result = "PASS"
    final_result = "PASS"

    if detector_ffc == "ΟΧΙ":
        final_result = "FAIL"

    if rh_result == "ΟΧΙ" or ag_result == "ΟΧΙ" or al_result == "ΟΧΙ":
        final_result = "FAIL"

    if fibers_2d < 5 or specs_2d < 4 or mass_2d < 4:
        result_2d = "FAIL"
        final_result = "FAIL"

    if fibers_dbt < 4 or specs_dbt < 4 or mass_dbt < 4:
        result_dbt = "FAIL"
        final_result = "FAIL"

    if snr_2d < 40:
        snr_result = "FAIL"
        final_result = "FAIL"

    new_row = pd.DataFrame([{
        "Date": qc_date,
        "Centre": centre,
        "Radiographer": radiographer,

        "Detector Flat Field Calibration": detector_ffc,

        "Artifact Rh kV": rh_kv,
        "Artifact Rh mAs": rh_mas,
        "Artifact Rh Result": rh_result,

        "Artifact Ag kV": ag_kv,
        "Artifact Ag mAs": ag_mas,
        "Artifact Ag Result": ag_result,

        "Artifact Al kV": al_kv,
        "Artifact Al mAs": al_mas,
        "Artifact Al Result": al_result,

        "2D kV": kv_2d,
        "2D mAs": mas_2d,
        "2D AGD": agd_2d,
        "2D Fibers": fibers_2d,
        "2D Specs": specs_2d,
        "2D Mass": mass_2d,
        "2D Result": result_2d,

        "DBT kV": kv_dbt,
        "DBT mAs": mas_dbt,
        "DBT AGD": agd_dbt,
        "DBT Fibers": fibers_dbt,
        "DBT Specs": specs_dbt,
        "DBT Mass": mass_dbt,
        "DBT Result": result_dbt,

        "2D SNR": snr_2d,
        "SNR Result": snr_result,

        "Comments": comments,
        "Final Result": final_result
    }])

    sheet = connect_to_gsheet()
    sheet.append_row(list(new_row.iloc[0].astype(str)))

    if final_result == "PASS":
        st.success("Ο εβδομαδιαίος έλεγχος καταχωρήθηκε επιτυχώς: PASS")
    else:
        st.error("Ο εβδομαδιαίος έλεγχος καταχωρήθηκε: FAIL")
        st.warning("Σύμφωνα με το πρωτόκολλο, σε περίπτωση ελέγχου εκτός ορίων πρέπει να ειδοποιείται ο/η υπεύθυνος/η Ιατροφυσικός.")

st.divider()

st.subheader("Ιστορικό Εβδομαδιαίων QC Ελέγχων")

sheet = connect_to_gsheet()
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty or "Final Result" not in df.columns:
    st.info("Δεν υπάρχουν ακόμα καταχωρημένοι εβδομαδιαίοι QC έλεγχοι.")
else:
    valid_df = df[
        (df["Radiographer"] != "") &
        (df["2D Fibers"].astype(str) != "0") &
        (df["DBT Fibers"].astype(str) != "0")
    ]

    st.metric("Total QC Submissions", len(valid_df))

    pass_count = len(valid_df[valid_df["Final Result"] == "PASS"])
    fail_count = len(valid_df[valid_df["Final Result"] == "FAIL"])

    col1, col2 = st.columns(2)

    with col1:
        st.metric("PASS", pass_count)

    with col2:
        st.metric("FAIL", fail_count)

    display_columns = [
        "Date",
        "Centre",
        "Radiographer",
        "2D Result",
        "DBT Result",
        "SNR Result",
        "Final Result"
    ]

    available_columns = [col for col in display_columns if col in df.columns]

    st.dataframe(
        valid_df[available_columns],
        use_container_width=True
    )