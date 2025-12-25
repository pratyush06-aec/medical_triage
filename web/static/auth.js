// async function login() {
//     const email = document.getElementById("email").value;
//     const password = document.getElementById("password").value;

//     const res = await fetch("/auth/login", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         credentials: "include",   // ✅ REQUIRED for session
//         body: JSON.stringify({ email, password })
//     });

//     const data = await res.json();

//     if (data.error) {
//         alert(data.error);
//         return;
//     }

//     // ✅ REQUIRED: move to authenticated app shell
//     window.location.href = "/";
// }

// async function signup() {
//     const email = document.getElementById("email").value;
//     const password = document.getElementById("password").value;

//     // 1️⃣ Register
//     const registerRes = await fetch("/auth/register", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         credentials: "include",
//         body: JSON.stringify({ email, password })
//     });

//     const registerData = await registerRes.json();

//     if (registerData.error) {
//         alert(registerData.error);
//         return;
//     }

//     // 2️⃣ IMMEDIATELY login (guaranteed session)
//     const loginRes = await fetch("/auth/login", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         credentials: "include",
//         body: JSON.stringify({ email, password })
//     });

//     const loginData = await loginRes.json();

//     if (loginData.error) {
//         alert("Signup succeeded, but login failed. Please login manually.");
//         return;
//     }

//     // 3️⃣ Enter app
//     window.location.href = "/";
// }











function setLoading(button, isLoading) {
    if (!button) return;
    button.disabled = isLoading;
    button.innerText = isLoading ? "Please wait…" : button.dataset.label;
}

function showError(message) {
    const el = document.getElementById("auth-error");
    if (!el) return;
    el.innerText = message;
    el.style.display = "block";
}

function clearError() {
    const el = document.getElementById("auth-error");
    if (!el) return;
    el.innerText = "";
    el.style.display = "none";
}

async function login() {
    clearError();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const btn = document.getElementById("loginBtn");

    if (!email || !password) {
        showError("Please enter both email and password.");
        return;
    }

    setLoading(btn, true);

    const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok || data.error) {
        showError(data.error || "Unable to login.");
        setLoading(btn, false);
        return;
    }

    window.location.href = "/";
}

async function signup() {
    clearError();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const btn = document.getElementById("signupBtn");

    if (!email || password.length < 6) {
        showError("Password must be at least 6 characters.");
        return;
    }

    setLoading(btn, true);

    await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password })
    });

    const loginRes = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password })
    });

    if (!loginRes.ok) {
        showError("Signup succeeded, but login failed.");
        setLoading(btn, false);
        return;
    }

    window.location.href = "/";
}

