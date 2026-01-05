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

function formatBotMessage(text) {
    // Escape HTML
    let safe = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Bold (**text**)
    safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Normalize ALL bullet styles to •
    // Handles: "- item", "• item", "* item"
    safe = safe.replace(/(^|\n|\<br\>|\s)[\-\*\•]\s+/g, "$1• ");

    // Break bullets onto new lines
    safe = safe.replace(/•\s+/g, "<br>• ");

    // Section emojis spacing
    safe = safe.replace(/(🩺)/g, "<br>$1");

    // Numbered options spacing
    safe = safe.replace(/(\d️⃣)/g, "<br>$1");

    // Clean excessive breaks
    safe = safe.replace(/(<br>\s*){3,}/g, "<br><br>");

    // Preserve real newlines
    safe = safe.replace(/\n+/g, "<br>");

    return safe.trim();
}





function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const wrapper = document.createElement("div");

    // 🎨 animation hook
    wrapper.classList.add(sender === "user" ? "user-msg" : "bot-msg");

    if (sender === "user") {
        wrapper.classList.add("flex", "justify-end");
        wrapper.innerHTML = `
            <div class="max-w-[75%] bg-blue-600 text-white px-4 py-2 rounded-lg text-sm leading-relaxed">
                ${text}
            </div>`;
    } else {
        wrapper.classList.add("flex", "justify-start");
        wrapper.innerHTML = `
            <div class="max-w-[75%] bg-emerald-50 border border-emerald-200 px-4 py-2 rounded-lg text-sm leading-relaxed">
                ${formatBotMessage(text)}
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
