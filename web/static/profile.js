document.addEventListener("DOMContentLoaded", loadAppointments);

async function loadAppointments() {
  const res = await fetch("/auth/profile/appointments", {
    credentials: "include"
  });

  if (res.status === 401) {
    window.location.href = "/static/auth.html";
    return;
  }

  const data = await res.json();
  render("upcoming-appointments", data.upcoming);
  render("past-appointments", data.past);
}

function render(id, items) {
  const ul = document.getElementById(id);
  ul.innerHTML = "";

  if (!items || items.length === 0) {
    ul.innerHTML = "<li>No appointments</li>";
    return;
  }

  items.forEach(a => {
    const li = document.createElement("li");

    // =================================================
    // ❌ OLD LOGIC (TEXT ONLY — COMMENTED, NOT DELETED)
    // -------------------------------------------------
    // li.textContent = `${a.date} ${a.time} • Dr ${a.doctor}`;
    // ul.appendChild(li);
    // =================================================


    // =================================================
    // ✅ MODIFICATION STARTS HERE
    // -------------------------------------------------

    // Resolve appointment ID safely (schema-safe)
    const appointmentId = a.appointment_id ?? a.id;

    // // Appointment text
    // const info = document.createElement("span");
    // info.textContent = `${a.date} ${a.time} • Dr ${a.doctor}`;
    // li.appendChild(info);

    // Appointment text
    const info = document.createElement("span");
    info.textContent = `${a.doctor} — ${a.date} (${a.time})`;
    li.appendChild(info);


    // 🔴 Cancel button (ONLY for upcoming appointments)
    if (id === "upcoming-appointments") {
      const cancelBtn = document.createElement("button");
      cancelBtn.textContent = "Cancel";
      cancelBtn.style.marginLeft = "10px";

      console.log("Cancel clicked for ID:", appointmentId);

      cancelBtn.onclick = () => cancelAppointment(appointmentId);

      li.appendChild(cancelBtn);
    }

    // =================================================
    // ✅ MODIFICATION ENDS HERE
    // =================================================

    ul.appendChild(li);
  });
}

function goBack() {
  window.location.href = "/";
}


// =================================================
// 🔴 CANCEL APPOINTMENT HANDLER
// =================================================
async function cancelAppointment(appointmentId) {
  if (!appointmentId) {
    alert("Invalid appointment");
    return;
  }

  const confirmCancel = confirm(
    "Are you sure you want to cancel this appointment?"
  );

  if (!confirmCancel) return;

  const res = await fetch(`/booking/cancel/${appointmentId}`, {
    method: "POST",
    credentials: "include"
  });

  if (!res.ok) {
    alert("Failed to cancel appointment");
    return;
  }

  const data = await res.json();

  if (data.success) {
    alert("Appointment cancelled");
    location.reload(); // simple & safe refresh
  } else {
    alert("Could not cancel appointment");
  }
}

