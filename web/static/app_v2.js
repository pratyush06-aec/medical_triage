// /*************************************************
//  * ✅ BOOTSTRAP (MODIFIED — PROFILE FLOW RESTORED)
//  *************************************************/
// document.addEventListener("DOMContentLoaded", async () => {
//     const authView = document.getElementById("auth-view");
//     const chatView = document.getElementById("chat-view");
//     const profileView = document.getElementById("profile-view");

//     // 🔒 Hide everything until auth is verified
//     authView.style.display = "none";
//     chatView.style.display = "none";
//     if (profileView) profileView.style.display = "none";

//     /*
//      * 🔧 MODIFICATION:
//      * Use /auth/me as the SINGLE source of truth
//      */
//     await checkAuth();

//     /*
//      * ❌ OLD PROFILE NAVIGATION (COMMENTED — DO NOT DELETE)
//      * Previously caused /profile → 404
//      */
//     /*
//     const profileToggleBtn = document.getElementById("profile-toggle");
//     if (profileToggleBtn) {
//         profileToggleBtn.addEventListener("click", () => {
//             window.location.href = "/profile";
//         });
//     }
//     */

//     /*
//      * ❌ OLD PROFILE PANEL TOGGLE WIRING (COMMENTED — DO NOT DELETE)
//      */
//     /*
//     const profileBtn = document.getElementById("profileBtn");
//     if (profileBtn) {
//         profileBtn.addEventListener("click", toggleProfile);
//     }
//     */

//     /*
//      * ✅ MODIFICATION (PROFILE BUTTON DETECTION)
//      */
//     const profileBtn = document.getElementById("profileBtn");
//     console.log("PROFILE BUTTON FOUND:", profileBtn);

//     /*
//      * ❌ DEBUG-ONLY CLICK HANDLER (COMMENTED — DO NOT DELETE)
//      */
//     /*
//     if (profileBtn) {
//         profileBtn.addEventListener("click", async () => {
//             console.log("✅ PROFILE CLICKED (DEBUG ONLY)");
//         });
//     }
//     */

//     /*
//      * ✅ FINAL PROFILE CLICK HANDLER
//      * MODIFICATION (CRITICAL):
//      * - Switches chat-view OFF
//      * - Switches profile-view ON
//      * - Fetches appointments
//      * - Renders into #profileContent
//      */
//     if (profileBtn) {
//         profileBtn.addEventListener("click", async () => {
//             console.log("➡️ Loading profile data...");

//             const res = await fetch("/auth/profile/appointments", {
//                 credentials: "include"
//             });

//             if (!res.ok) {
//                 window.location.href = "/login";
//                 return;
//             }

//             const data = await res.json();

//             // 🔁 VIEW SWITCH (PROFILE)
//             document.getElementById("chat-view").style.display = "none";
//             document.getElementById("profile-view").style.display = "block";

//             renderProfile(data);
//         });
//     }

//     /*
//      * ✅ BACK TO CHAT BUTTON (YOUR MODIFICATION)
//      * MODIFICATION:
//      * - Hides profile-view
//      * - Restores chat-view
//      */
//     const backBtn = document.getElementById("backToChatBtn");

//     if (backBtn) {
//         backBtn.addEventListener("click", () => {
//             document.getElementById("profile-view").style.display = "none";
//             document.getElementById("chat-view").style.display = "block";
//         });
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


// /*************************************************
//  * ✅ NEW AUTH CHECK (AUTHORITATIVE)
//  *************************************************/
// async function checkAuth() {
//     let res;

//     try {
//         res = await fetch("/auth/me", {
//             credentials: "include"
//         });
//     } catch {
//         window.location.href = "/login";
//         return;
//     }

//     if (!res.ok) {
//         window.location.href = "/login";
//         return;
//     }

//     const user = await res.json();
//     initApp(user);
// }


// /*************************************************
//  * ❌ OLD AUTH VIEW RENDERING (COMMENTED — DO NOT DELETE)
//  *************************************************/
// /*
// function showAuth() {
//     document.getElementById("chat-view").style.display = "none";
//     document.getElementById("auth-view").style.display = "flex";
// }
// */


// /*************************************************
//  * ✅ APP INITIALIZATION
//  *************************************************/
// function initApp(user) {
//     const logoutBtn = document.getElementById("logoutBtn");
//     const profileBtn = document.getElementById("profileBtn");

//     if (logoutBtn) logoutBtn.style.display = "block";
//     if (profileBtn) profileBtn.style.display = "block";

//     console.log("✅ Logged in as:", user.email);

//     showChat();
// }


// /*************************************************
//  * ✅ CHAT VIEW
//  *************************************************/
// function showChat() {
//     document.getElementById("auth-view").style.display = "none";
//     document.getElementById("chat-view").style.display = "block";
// }


// /*************************************************
//  * ❌ OLD PROFILE / FETCH / RENDER LOGIC
//  * COMMENTED — DO NOT DELETE
//  *************************************************/
// /*
// async function toggleProfile() {}
// function renderAppointments(...) {}
// */


// /*************************************************
//  * ✅ PROFILE RENDERER (FINAL — SEPARATE VIEW)
//  *************************************************/
// function renderProfile(data) {
//     const container = document.getElementById("profileContent");

//     container.innerHTML = `
//         <h3 class="font-medium text-green-600 mb-1">Upcoming</h3>
//         <ul class="mb-4">
//             ${
//                 data.upcoming.length
//                     ? data.upcoming.map(a => {
//                             const apptId = a.appointment_id ?? a.id;

//                             return `
//                                 <li class="flex items-center justify-between mb-2">
//                                     <span>${a.doctor} — ${a.date} ${a.time}</span>
//                                     <button
//                                         class="text-sm bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded"
//                                         onclick="cancelFromProfile(${apptId})">
//                                         Cancel
//                                     </button>
//                                 </li>
//                             `;
//                         }).join("")

//                     : "<li>No upcoming appointments</li>"
//             }
//         </ul>

//         <h3 class="font-medium text-gray-600 mb-1">Past</h3>
//         <ul>
//             ${
//                 data.past.length
//                     ? data.past.map(a =>
//                         `<li>${a.doctor} — ${a.date} ${a.time}</li>`
//                       ).join("")
//                     : "<li>No past appointments</li>"
//             }
//         </ul>
//     `;
// }

// async function cancelFromProfile(appointmentId) {
//     if (!appointmentId) return;

//     const confirmCancel = confirm(
//         "Are you sure you want to cancel this appointment?"
//     );
//     if (!confirmCancel) return;

//     const res = await fetch(
//         `/auth/profile/cancel/${appointmentId}`,
//         {
//             method: "POST",
//             credentials: "include"
//         }
//     );

//     if (!res.ok) {
//         alert("Failed to cancel appointment");
//         return;
//     }

//     // Reload profile data safely
//     const refreshed = await fetch("/auth/profile/appointments", {
//         credentials: "include"
//     });
//     const data = await refreshed.json();

//     renderProfile(data);
// }


// /*************************************************
//  * ❌ OLD LOGOUT (COMMENTED — DO NOT DELETE)
//  *************************************************/
// /*
// async function logout() {
//     await fetch("/auth/logout", {
//         method: "POST",
//         credentials: "same-origin"
//     });
// }
// */


// /*************************************************
//  * ✅ LOGOUT (FINAL)
//  *************************************************/
// async function logout() {
//     await fetch("/auth/logout", {
//         method: "POST",
//         credentials: "include"
//     });

//     window.location.href = "/login";
// }


// /*************************************************
//  * ❌ CHAT LOGIC (UNCHANGED)
//  *************************************************/
// async function sendMessage() {
//     const input = document.getElementById("user-input");
//     const message = input.value.trim();
//     if (!message) return;

//     addMessage(message, "user");
//     input.value = "";

//     const response = await fetch("/interact", {
//         method: "POST",
//         credentials: "same-origin",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message })
//     });

//     if (response.status === 401) {
//         window.location.href = "/login";
//         return;
//     }

//     const data = await response.json();
//     if (data?.reply) {
//         addMessage(data.reply, "bot");
//     }
// }


// function addMessage(text, sender) {
//     const chatBox = document.getElementById("chat-box");
//     const div = document.createElement("div");

//     div.className = sender === "user"
//         ? "user-message"
//         : "bot-message";

//     div.innerText = text;
//     chatBox.appendChild(div);
//     chatBox.scrollTop = chatBox.scrollHeight;
// }






















document.addEventListener("DOMContentLoaded", async () => {
    const authView = document.getElementById("auth-view");
    const chatView = document.getElementById("chat-view");
    const profileView = document.getElementById("profile-view");

    authView.style.display = "none";
    chatView.style.display = "none";
    if (profileView) profileView.style.display = "none";

    await checkAuth();

    const profileBtn = document.getElementById("profileBtn");
    if (profileBtn) {
        profileBtn.addEventListener("click", async () => {
            const res = await fetch("/auth/profile/appointments", {
                credentials: "include"
            });

            if (!res.ok) {
                window.location.href = "/login";
                return;
            }

            const data = await res.json();

            chatView.style.display = "none";
            profileView.style.display = "block";
            profileView.classList.add("view-transition"); // 🎨 UI only

            renderProfile(data);
        });
    }

    const backBtn = document.getElementById("backToChatBtn");
    if (backBtn) {
        backBtn.addEventListener("click", () => {
            profileView.style.display = "none";
            chatView.style.display = "block";
            chatView.classList.add("view-transition"); // 🎨 UI only
        });
    }
});

async function checkAuth() {
    const res = await fetch("/auth/me", { credentials: "include" });
    if (!res.ok) {
        window.location.href = "/login";
        return;
    }
    await res.json();
    showChat();
}

function showChat() {
    document.getElementById("chat-view").style.display = "block";
}

/* ================= CHAT ================= */

function showTypingIndicator() {
    const chatBox = document.getElementById("chat-box");
    const thinkingBar = document.getElementById("thinking-bar");

    const div = document.createElement("div");
    div.id = "typing-indicator";
    div.className = "thinking text-sm text-gray-500 italic";
    div.innerText = "Reviewing symptoms…";

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;

    // 🎨 Signature UX: show system thinking bar
    if (thinkingBar) thinkingBar.classList.remove("hidden");
}

function removeTypingIndicator() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();

    const thinkingBar = document.getElementById("thinking-bar");
    if (thinkingBar) thinkingBar.classList.add("hidden");
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    showTypingIndicator();

    const response = await fetch("/interact", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    removeTypingIndicator();

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
    const wrapper = document.createElement("div");

    // 🎨 animation hook
    wrapper.classList.add(sender === "user" ? "user-msg" : "bot-msg");

    if (sender === "user") {
        wrapper.classList.add("flex", "justify-end");
        wrapper.innerHTML = `
            <div class="max-w-[75%] bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">
                ${text}
            </div>`;
    } else {
        wrapper.classList.add("flex", "justify-start");
        wrapper.innerHTML = `
            <div class="max-w-[75%] bg-emerald-50 border border-emerald-200 px-4 py-2 rounded-lg text-sm">
                ${text}
            </div>`;
    }

    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

/* ================= PROFILE ================= */

function renderProfile(data) {
    const container = document.getElementById("profileContent");

    container.innerHTML = `
        <section class="mb-6">
            <h3 class="text-sm font-semibold text-emerald-700 mb-3">
                Upcoming Appointments
            </h3>
            ${
                data.upcoming.length
                    ? data.upcoming.map(a => {
                        const id = a.appointment_id ?? a.id;
                        return `
                            <div class="appointment-card border border-gray-200 rounded-lg p-3 mb-3 flex justify-between">
                                <div>
                                    <div class="font-medium">${a.doctor}</div>
                                    <div class="text-gray-600">${a.date} • ${a.time}</div>
                                </div>
                                <button
                                    class="text-sm text-red-600 hover:underline"
                                    onclick="cancelFromProfile(${id})">
                                    Cancel
                                </button>
                            </div>`;
                    }).join("")
                    : `<div class="text-sm text-gray-500">No upcoming appointments</div>`
            }
        </section>

        <section>
            <h3 class="text-sm font-semibold text-gray-700 mb-3">
                Past Appointments
            </h3>
            ${
                data.past.length
                    ? data.past.map(a => `
                        <div class="text-sm text-gray-600 mb-2">
                            ${a.doctor} — ${a.date} ${a.time}
                        </div>
                    `).join("")
                    : `<div class="text-sm text-gray-500">No past appointments</div>`
            }
        </section>
    `;
}

async function cancelFromProfile(id) {
    const confirmCancel = confirm(
        "Are you sure you want to cancel this appointment? This action cannot be undone."
    );
    if (!confirmCancel) return;

    const res = await fetch(`/auth/profile/cancel/${id}`, {
        method: "POST",
        credentials: "include"
    });

    if (!res.ok) {
        alert("Failed to cancel appointment");
        return;
    }

    const refreshed = await fetch("/auth/profile/appointments", {
        credentials: "include"
    });
    const data = await refreshed.json();
    renderProfile(data);
}

async function logout() {
    await fetch("/auth/logout", {
        method: "POST",
        credentials: "include"
    });
    window.location.href = "/login";
}
