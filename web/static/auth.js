// async function login() {
//   const email = document.getElementById("email").value;
//   const password = document.getElementById("password").value;

//   const res = await fetch("/auth/login", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ email, password })
//   });

//   const data = await res.json();

//   if (data.error) {
//     document.getElementById("auth-error").innerText = data.error;
//   } else {
//     location.reload();
//   }
// }

// async function signup() {
//   const email = document.getElementById("email").value;
//   const password = document.getElementById("password").value;

//   const res = await fetch("/auth/register", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ email, password })
//   });

//   const data = await res.json();

//   if (data.error) {
//     document.getElementById("auth-error").innerText = data.error;
//   } else {
//     location.reload();
//   }
// }












/*************************************************
 * ❌ OLD LOGIN & SIGNUP LOGIC (COMMENTED — DO NOT DELETE)
 *************************************************/
/*
async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (data.error) {
    document.getElementById("auth-error").innerText = data.error;
  } else {
    location.reload();
  }
}

async function signup() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (data.error) {
    document.getElementById("auth-error").innerText = data.error;
  } else {
    location.reload();
  }
}
*/


/*************************************************
 * ❌ PREVIOUS ATTEMPT (COMMENTED — CAUSED LOGIN LOOP)
 *************************************************
 * This version relied on backend redirect,
 * which DOES NOT work with fetch()
 *************************************************/
/*
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
        alert("Login failed");
    }
}
*/


/*************************************************
 * ✅ FINAL LOGIN & SIGNUP LOGIC (CORRECT)
 *************************************************
 * 🔧 MODIFICATIONS:
 * - Uses JSON-only backend response: { ok: true }
 * - Explicit frontend redirect after success
 * - credentials: "include" ensures session cookie
 * - NO reloads
 *************************************************/

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",   // ✅ REQUIRED for session
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    // ✅ REQUIRED: move to authenticated app shell
    window.location.href = "/";
}

async function signup() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",   // ✅ REQUIRED
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    // 🔧 MODIFICATION:
    // Auto-login behavior NOT assumed
    // User explicitly logs in after signup
    alert("Signup successful. Please login.");
}

