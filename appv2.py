from datetime import datetime
import streamlit as st
import sqlite3

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="Intermex Travel Center ICS050",
    layout="wide"
)

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    padding-top: 1rem;
}

.stApp {
background: linear-gradient(
135deg,
#F4F6F8,
#E9EEF4
);

</style>
""", unsafe_allow_html=True)

# ==================================================
# BASE DE DATOS
# ==================================================

conn = sqlite3.connect(
    "travel_operations.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ==================================================
# TITULO
# ==================================================

st.image(
    "logo.png",
    width=250
)

st.title("Check-In Center ICS050 ✈️")

st.caption(
    "Control Operativo de Check-In y Seguimiento de Viajes"
)

# ==================================================
# SIDEBAR
# ==================================================

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

    fecha_checkin = st.date_input(
        "Fecha Check In"
    )

    fecha_vuelo = st.date_input(
        "Fecha Vuelo"
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
                fecha_checkin.strftime("%Y-%m-%d"),
                fecha_vuelo.strftime("%Y-%m-%d"),
                comentarios
            )
        )

        conn.commit()

        st.success(
            "✅ Ticket guardado"
        )

# ==================================================
# DATOS
# ==================================================

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

# ==================================================
# KANBAN
# ==================================================

emitidos = []
disponibles = []
urgentes = []
realizados = []
completados = []

hoy = datetime.now().date()

for ticket in tickets:

    try:
        fecha_checkin = datetime.strptime(
            str(ticket[4]),
            "%d-%b-%Y"
        ).date()
    except:
        fecha_checkin = datetime.strptime(
            str(ticket[4]),
            "%Y-%m-%d"
        ).date()

    try:
        fecha_vuelo = datetime.strptime(
            str(ticket[5]),
            "%d-%b-%Y"
        ).date()
    except:
        fecha_vuelo = datetime.strptime(
            str(ticket[5]),
            "%Y-%m-%d"
        ).date()

    dias_para_vuelo = (
        fecha_vuelo - hoy
    ).days

    estado = "emitido"

    # El vuelo ya pasó
    if fecha_vuelo < hoy:
        estado = "completado"

    # Check-in realizado manualmente
    elif ticket[6] == "realizado":
        estado = "realizado"

    # Falta 1 día o menos para el vuelo
    elif dias_para_vuelo <= 1:
        estado = "urgente"

    # Ya se abrió el check-in
    elif hoy >= fecha_checkin:
        estado = "disponible"

    if estado == "emitido":

        emitidos.append(ticket)

    elif estado == "disponible":

        disponibles.append(ticket)

    elif estado == "urgente":

        urgentes.append(ticket)

    elif estado == "realizado":

        realizados.append(ticket)

    elif estado == "completado":

        completados.append(ticket)

# ==================================================
# KPIS
# ==================================================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "📋 Total Tickets",
        len(tickets)
    )

with c2:
    st.metric("🟡 Disponible", len(disponibles))

with c3:
    st.metric("🔴 Urgente", len(urgentes))

with c4:
    st.metric("✅🎫 Realizado", len(realizados))

with c5:
    st.metric("✈️ Completado", len(completados))

st.markdown("---")

# ==================================================
# EDITAR TICKET
# ==================================================

if "ticket_editar" in st.session_state:

    ticket_id = st.session_state["ticket_editar"]

    ticket = cursor.execute(
        """
        SELECT
            id,
            pasajero,
            aerolinea,
            pnr,
            fecha_checkin,
            fecha_vuelo,
            comentarios
        FROM checkins
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    st.subheader("✏️ Editar Ticket")

    pasajero_edit = st.text_input(
        "Pasajero",
        value=ticket[1]
    )

    aerolinea_edit = st.selectbox(
        "Aerolínea",
        ["VIVA", "VOLARIS", "AEROMEXICO", "OTRA"],
        index=["VIVA", "VOLARIS", "AEROMEXICO", "OTRA"].index(ticket[2])
    )

    pnr_edit = st.text_input(
        "PNR",
        value=ticket[3]
    )

    fecha_checkin_edit = st.date_input(
        "Fecha Check In",
        value=datetime.strptime(
            ticket[4],
            "%Y-%m-%d"
        ).date()
    )

    fecha_vuelo_edit = st.date_input(
        "Fecha Vuelo",
        value=datetime.strptime(
            ticket[5],
            "%Y-%m-%d"
        ).date()
    )

    comentarios_edit = st.text_area(
        "Comentarios",
        value=ticket[6]
    )

    col_g1, col_g2 = st.columns(2)

    with col_g1:

        if st.button("💾 Guardar Cambios"):

            cursor.execute(
                """
                UPDATE checkins
                SET
                    pasajero=?,
                    aerolinea=?,
                    pnr=?,
                    fecha_checkin=?,
                    fecha_vuelo=?,
                    comentarios=?
                WHERE id=?
                """,
                (
                    pasajero_edit,
                    aerolinea_edit,
                    pnr_edit,
                    fecha_checkin_edit.strftime("%Y-%m-%d"),
                    fecha_vuelo_edit.strftime("%Y-%m-%d"),
                    comentarios_edit,
                    ticket_id
                )
            )

            conn.commit()

            del st.session_state["ticket_editar"]

            st.success(
                "✅ Ticket actualizado"
            )

            st.rerun()

    with col_g2:

        if st.button("❌ Cancelar"):

            del st.session_state["ticket_editar"]

            st.rerun()

    st.markdown("---")

# ==================================================
# COLUMNAS KANBAN
# ==================================================

col1, col2, col3, col4, col5 = st.columns(5)

# ==================================================
# EMITIDOS
# ==================================================

with col1:

    st.subheader("🔵 Emitidos")

    for t in emitidos:

        st.success(
            f"""
👤 {t[1]}

✈️ {t[2]}

🎫 {t[3]}

📅 {t[4]}

🛫 {t[5]}
"""
        )

        if st.button(
            "🗑️ Eliminar",
            key=f"delete_emitido_{t[0]}"
        ):

            cursor.execute(
                """
                DELETE FROM checkins
                WHERE id = ?
                """,
                (t[0],)
            )

            conn.commit()

            st.rerun()

        if st.button(
            "✏️ Editar",
            key=f"editar_disp_{t[0]}"
        ):
            st.session_state["ticket_editar"] = t[0]
            
# ==================================================
# DISPONIBLE
# ==================================================

with col2:

    st.subheader("🟡 Disponible")

    for t in disponibles:

        st.warning(
            f"""
👤 {t[1]}

✈️ {t[2]}

🎫 {t[3]}

📅 {t[4]}

🛫 {t[5]}
"""
        )

        if st.button(
            "🗑️ Eliminar",
            key=f"delete_disponible_{t[0]}"
        ):

            cursor.execute(
                """
                DELETE FROM checkins
                WHERE id = ?
                """,
                (t[0],)
            )

            conn.commit()
            st.rerun()

        if st.button(
            "✅ Realizar Check-In",
            key=f"realizar_disp_{t[0]}"
        ):

            cursor.execute(
                """
                UPDATE checkins
                SET estado='realizado'
                WHERE id=?
                """,
                (t[0],)
            )

            conn.commit()
            st.rerun()

        if st.button(
            "✏️ Editar",
            key=f"editar_disponible_{t[0]}"
        ):
            st.session_state["ticket_editar"] = t[0]

# ==================================================
# URGENTE
# ==================================================

with col3:

    st.subheader("🔴 Urgente")

    for t in urgentes:

        st.error(
            f"""
👤 {t[1]}

✈️ {t[2]}

🎫 {t[3]}

📅 {t[4]}

🛫 {t[5]}
"""
        )

        if st.button(
            "🗑️ Eliminar",
            key=f"delete_urgente_{t[0]}"
        ):

            cursor.execute(
                """
                DELETE FROM checkins
                WHERE id = ?
                """,
                (t[0],)
            )

            conn.commit()

            st.rerun()

        if st.button(
            "✅ Realizar Check-In",
            key=f"realizar_urg_{t[0]}"
        ):

            cursor.execute(
                """
                UPDATE checkins
                SET estado='realizado'
                WHERE id=?
                """,
                (t[0],)
           )

            conn.commit()
            st.rerun()

        if st.button(
            "✏️ Editar",
            key=f"editar_urgente_{t[0]}"
        ):
            st.session_state["ticket_editar"] = t[0]
# ==================================================
# REALIZADO
# ==================================================

with col4:

    st.subheader("✅ Realizado")

    for t in realizados:

        st.info(
            f"""
👤 {t[1]}

✈️ {t[2]}

🎫 {t[3]}
"""
        )

        if st.button(
            "🗑️ Eliminar",
            key=f"delete_realizado_{t[0]}"
        ):

            cursor.execute(
                """
                DELETE FROM checkins
                WHERE id = ?
                """,
                (t[0],)
            )

            conn.commit()

            st.rerun()

        if st.button(
            "✏️ Editar",
            key=f"editar_realizado_{t[0]}"
        ):
            st.session_state["ticket_editar"] = t[0]
# ==================================================
# COMPLETADO
# ==================================================

with col5:

    st.subheader("✈️ Completado")

    for t in completados:

        st.info(
            f"""
👤 {t[1]}

✈️ {t[2]}

🎫 {t[3]}
"""
        )

        if st.button(
            "🗑️ Eliminar",
            key=f"delete_completado_{t[0]}"
        ):

            cursor.execute(
                """
                DELETE FROM checkins
                WHERE id = ?
                """,
                (t[0],)
            )

            conn.commit()

            st.rerun()

        if st.button(
            "✏️ Editar",
            key=f"editar_completado_{t[0]}"
        ):
            st.session_state["ticket_editar"] = t[0]
