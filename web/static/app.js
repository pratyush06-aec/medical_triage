// /*************************************************
//  * ❌ OLD (COMMENTED — DO NOT DELETE)
//  *************************************************/
// // window.onload = checkAuth;


// /*************************************************
//  * ✅ BOOTSTRAP (MODIFIED — STEP 4 + PROFILE CLICK LOGIC)
//  *************************************************/
// document.addEventListener("DOMContentLoaded", async () => {
//     const authView = document.getElementById("auth-view");
//     const chatView = document.getElementById("chat-view");

//     // 🔒 Hide everything until auth is verified
//     authView.style.display = "none";
//     chatView.style.display = "none";

//     /*
//      * 🔧 MODIFICATION (STEP 4):
//      * Use /auth/me as the SINGLE source of truth
//      */
//     await checkAuth();

//     /*
//      * ❌ OLD PROFILE NAVIGATION (COMMENTED — DO NOT DELETE)
//      * Caused /profile → 404
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
//      * ✅ MODIFICATION (PROFILE — FINAL SPA FLOW)
//      * Profile button now:
//      *  - fetches /auth/profile/appointments
//      *  - renders profile inline
//      *  - NO navigation
//      */
//     const profileBtn = document.getElementById("profileBtn");

//     if (profileBtn) {
//         profileBtn.addEventListener("click", async () => {
//             const res = await fetch("/auth/profile/appointments", {
//                 credentials: "include"
//             });

//             if (!res.ok) {
//                 window.location.href = "/login";
//                 return;
//             }

//             const data = await res.json();
//             renderProfile(data);
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
//  * ✅ NEW AUTH CHECK (AUTHORITATIVE — STEP 4)
//  *************************************************/
// async function checkAuth() {
//     let res;

//     try {
//         res = await fetch("/auth/me", {
//             credentials: "include"
//         });
//     } catch (err) {
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

//     fetch("/static/auth.html")
//         .then(res => res.text())
//         .then(html => {
//             document.getElementById("auth-view").innerHTML = html;
//         });
// }
// */


// /*************************************************
//  * ✅ APP INITIALIZATION (MODIFIED — STEP 5)
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
//  * ✅ CHAT VIEW (SAFE — AUTH CONFIRMED)
//  *************************************************/
// function showChat() {
//     document.getElementById("auth-view").style.display = "none";
//     document.getElementById("chat-view").style.display = "block";
// }


// /*************************************************
//  * ❌ OLD PROFILE PANEL TOGGLE LOGIC (COMMENTED — DO NOT DELETE)
//  *************************************************/
// /*
// async function toggleProfile() {
//     const panel = document.getElementById("profile-panel");

//     if (!panel.classList.contains("hidden")) {
//         panel.classList.add("hidden");
//         return;
//     }

//     const res = await fetch("/auth/profile/appointments", {
//         credentials: "include"
//     });

//     if (!res.ok) {
//         window.location.href = "/login";
//         return;
//     }

//     const data = await res.json();

//     renderAppointments("upcoming-appointments", data.upcoming);
//     renderAppointments("past-appointments", data.past);

//     panel.classList.remove("hidden");
// }
// */


// /*************************************************
//  * ❌ OLD PROFILE RENDERER (COMMENTED — DO NOT DELETE)
//  *************************************************/
// /*
// function renderProfile(data) {
//     const container = document.getElementById("chat-view");
//     ...
// }
// */


// /*************************************************
//  * ✅ NEW PROFILE RENDERER (FINAL — USES mainContent)
//  *************************************************/
// function renderProfile(data) {
//     /*
//      * 🔧 MODIFICATION:
//      * Render profile into #mainContent instead of chat-view
//      * Preserves chat UI and keeps SPA layout clean
//      */
//     const container = document.getElementById("mainContent");

//     container.innerHTML = `
//         <h2>My Appointments</h2>

//         <h3>Upcoming</h3>
//         <ul>
//             ${
//                 data.upcoming.map(a =>
//                     `<li>${a.doctor} — ${a.date} ${a.time}</li>`
//                 ).join("")
//             }
//         </ul>

//         <h3>Past</h3>
//         <ul>
//             ${
//                 data.past.map(a =>
//                     `<li>${a.doctor} — ${a.date} ${a.time}</li>`
//                 ).join("")
//             }
//         </ul>
//     `;
// }


// /*************************************************
//  * ❌ OLD APPOINTMENT RENDERER (COMMENTED — DO NOT DELETE)
//  *************************************************/
// /*
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
//         li.textContent = `${a.date} ${a.time} • Dr ${a.doctor}`;
//         ul.appendChild(li);
//     });
// }
// */


// /*************************************************
//  * ❌ OLD LOGOUT (COMMENTED — DO NOT DELETE)
//  *************************************************/
// /*
// async function logout() {
//     await fetch("/auth/logout", {
//         method: "POST",
//         credentials: "same-origin"
//     });

//     window.location.href = "/login";
// }
// */


// /*************************************************
//  * ✅ LOGOUT (MODIFIED — FINAL)
//  *************************************************/
// async function logout() {
//     await fetch("/auth/logout", {
//         method: "POST",
//         credentials: "include"
//     });

//     window.location.href = "/login";
// }


// /*************************************************
//  * ✅ CHAT LOGIC (MODIFIED — STEP 6)
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










/*************************************************
 * ❌ OLD (COMMENTED — DO NOT DELETE)
 *************************************************/
// window.onload = checkAuth;


/*************************************************
 * ❌ DUPLICATE OLD (COMMENTED — DO NOT DELETE)
 *************************************************/
// window.onload = checkAuth;


/*************************************************
 * ✅ BOOTSTRAP (MODIFIED — PROFILE FLOW RESTORED)
 *************************************************/
document.addEventListener("DOMContentLoaded", async () => {
    const authView = document.getElementById("auth-view");
    const chatView = document.getElementById("chat-view");
    const profileView = document.getElementById("profile-view");

    // 🔒 Hide everything until auth is verified
    authView.style.display = "none";
    chatView.style.display = "none";
    if (profileView) profileView.style.display = "none";

    /*
     * 🔧 MODIFICATION:
     * Use /auth/me as the SINGLE source of truth
     */
    await checkAuth();

    /*
     * ❌ OLD PROFILE NAVIGATION (COMMENTED — DO NOT DELETE)
     * Previously caused /profile → 404
     */
    /*
    const profileToggleBtn = document.getElementById("profile-toggle");
    if (profileToggleBtn) {
        profileToggleBtn.addEventListener("click", () => {
            window.location.href = "/profile";
        });
    }
    */

    /*
     * ❌ OLD PROFILE PANEL TOGGLE WIRING (COMMENTED — DO NOT DELETE)
     */
    /*
    const profileBtn = document.getElementById("profileBtn");
    if (profileBtn) {
        profileBtn.addEventListener("click", toggleProfile);
    }
    */

    /*
     * ✅ MODIFICATION (PROFILE BUTTON DETECTION)
     */
    const profileBtn = document.getElementById("profileBtn");
    console.log("PROFILE BUTTON FOUND:", profileBtn);

    /*
     * ❌ DEBUG-ONLY CLICK HANDLER (COMMENTED — DO NOT DELETE)
     */
    /*
    if (profileBtn) {
        profileBtn.addEventListener("click", async () => {
            console.log("✅ PROFILE CLICKED (DEBUG ONLY)");
        });
    }
    */

    /*
     * ✅ FINAL PROFILE CLICK HANDLER
     * MODIFICATION (CRITICAL):
     * - Switches chat-view OFF
     * - Switches profile-view ON
     * - Fetches appointments
     * - Renders into #profileContent
     */
    if (profileBtn) {
        profileBtn.addEventListener("click", async () => {
            console.log("➡️ Loading profile data...");

            const res = await fetch("/auth/profile/appointments", {
                credentials: "include"
            });

            if (!res.ok) {
                window.location.href = "/login";
                return;
            }

            const data = await res.json();

            // 🔁 VIEW SWITCH (PROFILE)
            document.getElementById("chat-view").style.display = "none";
            document.getElementById("profile-view").style.display = "block";

            renderProfile(data);
        });
    }

    /*
     * ✅ BACK TO CHAT BUTTON (YOUR MODIFICATION)
     * MODIFICATION:
     * - Hides profile-view
     * - Restores chat-view
     */
    const backBtn = document.getElementById("backToChatBtn");

    if (backBtn) {
        backBtn.addEventListener("click", () => {
            document.getElementById("profile-view").style.display = "none";
            document.getElementById("chat-view").style.display = "block";
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
 * ✅ NEW AUTH CHECK (AUTHORITATIVE)
 *************************************************/
async function checkAuth() {
    let res;

    try {
        res = await fetch("/auth/me", {
            credentials: "include"
        });
    } catch {
        window.location.href = "/login";
        return;
    }

    if (!res.ok) {
        window.location.href = "/login";
        return;
    }

    const user = await res.json();
    initApp(user);
}


/*************************************************
 * ❌ OLD AUTH VIEW RENDERING (COMMENTED — DO NOT DELETE)
 *************************************************/
/*
function showAuth() {
    document.getElementById("chat-view").style.display = "none";
    document.getElementById("auth-view").style.display = "flex";
}
*/


/*************************************************
 * ✅ APP INITIALIZATION
 *************************************************/
function initApp(user) {
    const logoutBtn = document.getElementById("logoutBtn");
    const profileBtn = document.getElementById("profileBtn");

    if (logoutBtn) logoutBtn.style.display = "block";
    if (profileBtn) profileBtn.style.display = "block";

    console.log("✅ Logged in as:", user.email);

    showChat();
}


/*************************************************
 * ✅ CHAT VIEW
 *************************************************/
function showChat() {
    document.getElementById("auth-view").style.display = "none";
    document.getElementById("chat-view").style.display = "block";
}


/*************************************************
 * ❌ OLD PROFILE / FETCH / RENDER LOGIC
 * COMMENTED — DO NOT DELETE
 *************************************************/
/*
async function toggleProfile() {}
function renderAppointments(...) {}
*/


/*************************************************
 * ✅ PROFILE RENDERER (FINAL — SEPARATE VIEW)
 *************************************************/
function renderProfile(data) {
    const container = document.getElementById("profileContent");

    container.innerHTML = `
        <h3 class="font-medium text-green-600 mb-1">Upcoming</h3>
        <ul class="mb-4">
            ${
                data.upcoming.length
                    ? data.upcoming.map(a => {
                            const apptId = a.appointment_id ?? a.id;

                            return `
                                <li class="flex items-center justify-between mb-2">
                                    <span>${a.doctor} — ${a.date} ${a.time}</span>
                                    <button
                                        class="text-sm bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded"
                                        onclick="cancelFromProfile(${apptId})">
                                        Cancel
                                    </button>
                                </li>
                            `;
                        }).join("")

                    : "<li>No upcoming appointments</li>"
            }
        </ul>

        <h3 class="font-medium text-gray-600 mb-1">Past</h3>
        <ul>
            ${
                data.past.length
                    ? data.past.map(a =>
                        `<li>${a.doctor} — ${a.date} ${a.time}</li>`
                      ).join("")
                    : "<li>No past appointments</li>"
            }
        </ul>
    `;
}

async function cancelFromProfile(appointmentId) {
    if (!appointmentId) return;

    const confirmCancel = confirm(
        "Are you sure you want to cancel this appointment?"
    );
    if (!confirmCancel) return;

    const res = await fetch(
        `/auth/profile/cancel/${appointmentId}`,
        {
            method: "POST",
            credentials: "include"
        }
    );

    if (!res.ok) {
        alert("Failed to cancel appointment");
        return;
    }

    // Reload profile data safely
    const refreshed = await fetch("/auth/profile/appointments", {
        credentials: "include"
    });
    const data = await refreshed.json();

    renderProfile(data);
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
}
*/


/*************************************************
 * ✅ LOGOUT (FINAL)
 *************************************************/
async function logout() {
    await fetch("/auth/logout", {
        method: "POST",
        credentials: "include"
    });

    window.location.href = "/login";
}


/*************************************************
 * ❌ CHAT LOGIC (UNCHANGED)
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


