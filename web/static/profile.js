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
    li.textContent = `${a.date} ${a.time} • Dr ${a.doctor}`;
    ul.appendChild(li);
  });
}

function goBack() {
  window.location.href = "/";
}

async function logout() {
  await fetch("/auth/logout", {
    method: "POST",
    credentials: "include"
  });
  window.location.href = "/static/auth.html";
}
