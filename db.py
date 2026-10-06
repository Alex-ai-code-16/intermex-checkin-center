import streamlit as st
import sqlite3

# ======================================
# CONFIG
# ======================================

st.set_page_config(
    page_title="Travel Operations Center",
    layout="wide"
)

# ======================================
# CONEXION DB
# ======================================

conn = sqlite3.connect(
    "database/travel_operations.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ======================================
# TITULO
# ======================================

st.title("✈️ Travel Operations Center")

# ======================================
# SIDEBAR
# ======================================

with st.sidebar:

    st.header("➕ Nuevo Ticket")

    pasajero = st.text_input("Pasajero")

    aerolinea = st.selectbox(
        "Aerolínea",
        [
            "VIVA",
            "VOLARIS",
            "AEROMEXICO",
            "OTRA"
        ]
    )

    pnr = st.text_input("PNR")

    fecha_checkin = st.text_input(
        "Fecha Check In",
        placeholder="07-Jan-2027"
    )

    fecha_vuelo = st.text_input(
        "Fecha Vuelo",
        placeholder="10-Jan-2027"
    )

    comentarios = st.text_area(
        "Comentarios"
    )

    if st.button("Guardar Ticket"):

        cursor.execute(
            """
            INSERT INTO checkins
            (
                pasajero,
                aerolinea,
                pnr,
                fecha_checkin,
                fecha_vuelo,
                comentarios
            )
            VALUES
            (?,?,?,?,?,?)
            """,
            (
                pasajero,
                aerolinea,
                pnr,
                fecha_checkin,
                fecha_vuelo,
                comentarios
            )
        )

        conn.commit()

        st.success(
            "✅ Ticket guardado"
        )

# ======================================
# KPI
# ======================================

total = cursor.execute(
    "SELECT COUNT(*) FROM checkins"
).fetchone()[0]

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric("🎫 Tickets", total)

with c2:
    st.metric("🟡 Disponible", 0)

with c3:
    st.metric("🔴 Urgente", 0)

with c4:
    st.metric("✅ Realizado", 0)

with c5:
    st.metric("✈️ Finalizado", 0)

st.markdown("---")

# ======================================
# TICKETS
# ======================================

st.subheader("🎫 Tickets")

tickets = cursor.execute(
    """
    SELECT
        id,
        pasajero,
        aerolinea,
        pnr,
        fecha_checkin,
        fecha_vuelo,
        estado,
        comentarios
    FROM checkins
    ORDER BY id DESC
    """
).fetchall()

for ticket in tickets:

    with st.container():

        st.info(
            f"""
👤 {ticket[1]}

✈️ {ticket[2]}

🎫 {ticket[3]}

📅 Check In:
{ticket[4]}

🛫 Vuelo:
{ticket[5]}

📝 {ticket[6]}
"""
        )