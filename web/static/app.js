// /*************************************************
//  * ❌ OLD (COMMENTED — DO NOT DELETE)
//  *************************************************/
// // window.onload = checkAuth;

// /*************************************************
//  * ✅ BOOTSTRAP
//  *************************************************/
// document.addEventListener("DOMContentLoaded", async () => {
//     const authView = document.getElementById("auth-view");
//     const chatView = document.getElementById("chat-view");

//     authView.style.display = "none";
//     chatView.style.display = "none";

//     // ❌ OLD AUTH CHECK (CAUSES 404 — DO NOT DELETE)
//     // await checkAuth();

//     // ✅ NEW: Directly show chat (session handled backend-side)
//     showChat();

//     // ✅ Profile toggle binding
//     const profileBtn = document.getElementById("profile-toggle");
//     if (profileBtn) {
//        profileBtn.addEventListener("click", () => {
//        window.location.href = "/static/profile.html";
// });

//     }
// });

// /*************************************************
//  * ❌ OLD AUTH CHECK (COMMENTED — DO NOT DELETE)
//  *************************************************/
// /*
// async function checkAuth() {
//     let res;
//     try {
//         res = await fetch("/auth/profile/me", {
//             credentials: "same-origin"
//         });
//     } catch {
//         showAuth();
//         return;
//     }

//     const data = await res.json();
//     if (data.error) {
//         showAuth();
//     } else {
//         showChat();
//     }
// }
// */

// function showAuth() {
//     document.getElementById("chat-view").style.display = "none";
//     document.getElementById("auth-view").style.display = "flex";

//     fetch("/static/auth.html")
//         .then(res => res.text())
//         .then(html => {
//             document.getElementById("auth-view").innerHTML = html;
//         });
// }

// function showChat() {
//     document.getElementById("auth-view").style.display = "none";
//     document.getElementById("chat-view").style.display = "block";
// }

// /*************************************************
//  * 👤 PROFILE PANEL LOGIC (FINAL)
//  *************************************************/
// async function toggleProfile() {
//     const panel = document.getElementById("profile-panel");

//     // Toggle close
//     if (!panel.classList.contains("hidden")) {
//         panel.classList.add("hidden");
//         return;
//     }

//     const res = await fetch("auth/profile/appointments", {
//         credentials: "same-origin"
//     });

//     if (!res.ok) {
//         console.error("Failed to load profile appointments");
//         return;
//     }

//     const data = await res.json();

//     renderAppointments("upcoming-appointments", data.upcoming);
//     renderAppointments("past-appointments", data.past);

//     panel.classList.remove("hidden");
// }

// function renderAppointments(elementId, appointments) {
//     const ul = document.getElementById(elementId);
//     ul.innerHTML = "";

//     if (!appointments || appointments.length === 0) {
//         const li = document.createElement("li");
//         li.textContent = "No appointments";
//         ul.appendChild(li);
//         return;
//     }

//     appointments.forEach(a => {
//         const li = document.createElement("li");

//         // ✅ FIX: backend does NOT return specialty
//         li.textContent = `${a.date} ${a.time} • Dr ${a.doctor}`;

//         ul.appendChild(li);
//     });
// }

// /*************************************************
//  * ✅ LOGOUT
//  *************************************************/
// async function logout() {
//     await fetch("/auth/logout", {
//         method: "POST",
//         credentials: "same-origin"
//     });
//     showAuth();
// }

// /*************************************************
//  * ✅ CHAT LOGIC (UNCHANGED)
//  *************************************************/
// async function sendMessage() {
//     const input = document.getElementById("user-input");
//     const message = input.value.trim();
//     if (!message) return;

//     addMessage(message, "user");
//     input.value = "";

//     const response = await fetch("/interact", {
//     method: "POST",
//     credentials: "same-origin", // ✅ ADD THIS
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ message })
//     });

//     const data = await response.json();
//     if (data?.reply) {
//         addMessage(data.reply, "bot");
//     }
// }

// function addMessage(text, sender) {
//     const chatBox = document.getElementById("chat-box");
//     const div = document.createElement("div");
//     div.className = sender === "user" ? "user-message" : "bot-message";
//     div.innerText = text;
//     chatBox.appendChild(div);
//     chatBox.scrollTop = chatBox.scrollHeight;
// }












/*************************************************
 * ❌ OLD (COMMENTED — DO NOT DELETE)
 *************************************************/
// window.onload = checkAuth;


/*************************************************
 * ✅ BOOTSTRAP (MODIFIED — STEP 4)
 *************************************************/
document.addEventListener("DOMContentLoaded", async () => {
    const authView = document.getElementById("auth-view");
    const chatView = document.getElementById("chat-view");

    // 🔒 Hide everything until auth is verified
    authView.style.display = "none";
    chatView.style.display = "none";

    /*
     * 🔧 MODIFICATION (STEP 4):
     * Use /auth/me as the SINGLE source of truth
     * Frontend renders NOTHING until auth is verified
     *
     * ⚠️ IMPORTANT:
     * Backend MUST expose GET /auth/me
     * which returns:
     *   200 + user JSON  → authenticated
     *   401 / 403        → unauthenticated
     */
    await checkAuth();

    /*
     * ✅ MODIFICATION:
     * Profile navigation via backend-protected route (/profile)
     */
    const profileToggleBtn = document.getElementById("profile-toggle");
    if (profileToggleBtn) {
        profileToggleBtn.addEventListener("click", () => {
            window.location.href = "/profile";
        });
    }
});


/*************************************************
 * ❌ OLD AUTH CHECK (COMMENTED — DO NOT DELETE)
 *************************************************/
/*
async function checkAuth() {
    let res;
    try {
        res = await fetch("/auth/profile/me", {
            credentials: "same-origin"
        });
    } catch {
        showAuth();
        return;
    }

    const data = await res.json();
    if (data.error) {
        showAuth();
    } else {
        showChat();
    }
}
*/


/*************************************************
 * ✅ NEW AUTH CHECK (AUTHORITATIVE — STEP 4)
 *************************************************/
async function checkAuth() {
    let res;

    try {
        res = await fetch("/auth/me", {
            credentials: "include"
        });
    } catch (err) {
        // Network / server error → force login
        window.location.href = "/login";
        return;
    }

    /*
     * 🔐 HARD REDIRECT — NO UI RENDERING
     * Backend controls auth state
     */
    if (!res.ok) {
        window.location.href = "/login";
        return;
    }

    const user = await res.json();

    /*
     * 🔧 MODIFICATION (STEP 5):
     * Initialize app ONLY after auth confirmed
     */
    initApp(user);
}


/*************************************************
 * ❌ OLD AUTH VIEW RENDERING (COMMENTED — DO NOT DELETE)
 *************************************************/
/*
function showAuth() {
    document.getElementById("chat-view").style.display = "none";
    document.getElementById("auth-view").style.display = "flex";

    fetch("/static/auth.html")
        .then(res => res.text())
        .then(html => {
            document.getElementById("auth-view").innerHTML = html;
        });
}
*/


/*************************************************
 * ✅ APP INITIALIZATION (MODIFIED — STEP 5)
 *************************************************/
function initApp(user) {
    /*
     * 🔧 MODIFICATION:
     * Show Logout & Profile buttons ONLY after auth is confirmed
     * ❌ No assumed-login UI anymore
     */
    const logoutBtn = document.getElementById("logoutBtn");
    const profileBtn = document.getElementById("profileBtn");

    if (logoutBtn) logoutBtn.style.display = "block";
    if (profileBtn) profileBtn.style.display = "block";

    // Optional: debug / greeting
    console.log("✅ Logged in as:", user.email);

    showChat();
}


/*************************************************
 * ✅ CHAT VIEW (SAFE — AUTH CONFIRMED)
 *************************************************/
function showChat() {
    document.getElementById("auth-view").style.display = "none";
    document.getElementById("chat-view").style.display = "block";
}


/*************************************************
 * 👤 PROFILE PANEL LOGIC (UNCHANGED)
 *************************************************/
async function toggleProfile() {
    const panel = document.getElementById("profile-panel");

    // Toggle close
    if (!panel.classList.contains("hidden")) {
        panel.classList.add("hidden");
        return;
    }

    const res = await fetch("/auth/profile/appointments", {
        credentials: "same-origin"
    });

    if (!res.ok) {
        console.error("Failed to load profile appointments");
        return;
    }

    const data = await res.json();

    renderAppointments("upcoming-appointments", data.upcoming);
    renderAppointments("past-appointments", data.past);

    panel.classList.remove("hidden");
}


function renderAppointments(elementId, appointments) {
    const ul = document.getElementById(elementId);
    ul.innerHTML = "";

    if (!appointments || appointments.length === 0) {
        const li = document.createElement("li");
        li.textContent = "No appointments";
        ul.appendChild(li);
        return;
    }

    appointments.forEach(a => {
        const li = document.createElement("li");

        // ✅ Backend does NOT return specialty
        li.textContent = `${a.date} ${a.time} • Dr ${a.doctor}`;

        ul.appendChild(li);
    });
}


/*************************************************
 * ❌ OLD LOGOUT (COMMENTED — DO NOT DELETE)
 *************************************************/
/*
async function logout() {
    await fetch("/auth/logout", {
        method: "POST",
        credentials: "same-origin"
    });

    window.location.href = "/login";
}
*/


/*************************************************
 * ✅ LOGOUT (MODIFIED — FINAL)
 *************************************************/
async function logout() {
    /*
     * 🔧 MODIFICATION:
     * Use credentials: "include" for consistency
     * with all session-based auth calls
     */
    await fetch("/auth/logout", {
        method: "POST",
        credentials: "include"
    });

    // 🔐 Backend controls routing
    window.location.href = "/login";
}


/*************************************************
 * ✅ CHAT LOGIC (MODIFIED — STEP 6)
 *************************************************/
async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    const response = await fetch("/interact", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    /*
     * 🔧 MODIFICATION (STEP 6):
     * Session expired / invalid → FORCE re-login
     */
    if (response.status === 401) {
        window.location.href = "/login";
        return;
    }

    const data = await response.json();
    if (data?.reply) {
        addMessage(data.reply, "bot");
    }
}


function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");

    div.className = sender === "user"
        ? "user-message"
        : "bot-message";

    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}
