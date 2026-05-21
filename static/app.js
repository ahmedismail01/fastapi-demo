const state = {
    token: localStorage.getItem("token"),
    user: null,
    users: [],
    postsTab: "feed",
    followings: [],
    followers: [],
    socket: null,
};

const $ = (selector) => document.querySelector(selector);

function authHeaders() {
    return state.token ? {Authorization: `Bearer ${state.token}`} : {};
}

function decodeToken(token) {
    if (!token) {
        return null;
    }

    try {
        const payload = token.split(".")[1] || "";
        const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
        const padded = normalized.padEnd(normalized.length + ((4 - normalized.length % 4) % 4), "=");
        const json = atob(padded);
        return JSON.parse(json);
    } catch {
        return null;
    }
}

function showToast(message, isError = false) {
    const toast = $("#toast");
    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.remove("hidden");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.add("hidden"), 3200);
}

async function request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    const body = options.body;

    Object.entries(authHeaders()).forEach(([key, value]) => headers.set(key, value));

    if (body && !(body instanceof URLSearchParams)) {
        headers.set("Content-Type", "application/json");
    }

    const response = await fetch(path, {
        ...options,
        headers,
        body: body && !(body instanceof URLSearchParams) ? JSON.stringify(body) : body,
    });

    let data = null;
    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
            clearSession();
            renderSignedOut();
        }
        throw new Error((data && data.detail) || "Request failed");
    }

    return data;
}

function clearSession() {
    localStorage.removeItem("token");
    state.token = null;
    state.user = null;
    state.users = [];
    state.followings = [];
    state.followers = [];
    if (state.socket) {
        state.socket.close();
        state.socket = null;
    }
}

function setSessionFromToken() {
    const payload = decodeToken(state.token);
    state.user = payload ? {id: Number(payload.id), email: payload.email} : null;
    $("#sessionLabel").textContent = state.user ? state.user.email : "Signed out";
    const isLoggedIn = Boolean(state.token && state.user);
    $("#logoutBtn").disabled = !isLoggedIn;
    $("#postTitle").disabled = !isLoggedIn;
    $("#postContent").disabled = !isLoggedIn;
    $("#postForm button[type='submit']").disabled = !isLoggedIn;
    $("#refreshUsersBtn").disabled = !isLoggedIn;
    $("#refreshPostsBtn").disabled = !isLoggedIn;
}

function setAuthTab(tab) {
    document.querySelectorAll("[data-auth-tab]").forEach((button) => {
        button.classList.toggle("active", button.dataset.authTab === tab);
    });
    $("#loginForm").classList.toggle("hidden", tab !== "login");
    $("#registerForm").classList.toggle("hidden", tab !== "register");
}

function setPostTab(tab) {
    state.postsTab = tab;
    document.querySelectorAll("[data-post-tab]").forEach((button) => {
        button.classList.toggle("active", button.dataset.postTab === tab);
    });
    loadPosts().catch((error) => showToast(error.message || "Could not load posts.", true));
}

function itemShell(className = "list-item") {
    const item = document.createElement("div");
    item.className = className;
    return item;
}

function renderEmpty(container, message) {
    container.className = container.className.replace(/\bempty\b/g, "").trim();
    container.classList.add("empty");
    container.textContent = message;
}

function renderUsers() {
    const usersList = $("#usersList");
    usersList.innerHTML = "";
    usersList.classList.remove("empty");

    if (!state.token) {
        renderEmpty(usersList, "Login to browse writers.");
        return;
    }

    const followedIds = new Set(state.followings.map((following) => following.user_id));
    const visibleUsers = state.users.filter((user) => user.id !== (state.user && state.user.id));

    if (!visibleUsers.length) {
        renderEmpty(usersList, "No other writers found.");
        return;
    }

    visibleUsers.forEach((user) => {
        const item = itemShell();
        const meta = document.createElement("div");
        const name = document.createElement("strong");
        const email = document.createElement("span");
        const button = document.createElement("button");

        name.textContent = user.name;
        email.textContent = user.email;
        button.className = followedIds.has(user.id) ? "ghost" : "";
        button.textContent = followedIds.has(user.id) ? "Unfollow" : "Follow";
        button.type = "button";
        button.addEventListener("click", () => toggleFollow(user.id, followedIds.has(user.id)));

        meta.append(name, email);
        item.append(meta, button);
        usersList.appendChild(item);
    });
}

function renderRelationshipList(containerSelector, countSelector, records, emptyMessage) {
    const container = $(containerSelector);
    const count = $(countSelector);
    container.innerHTML = "";
    container.classList.remove("empty");
    count.textContent = records.length;

    if (!records.length) {
        renderEmpty(container, emptyMessage);
        return;
    }

    records.forEach((record) => {
        const item = itemShell();
        const meta = document.createElement("div");
        const name = document.createElement("strong");
        const email = document.createElement("span");
        const user = record.user || {};

        name.textContent = user.name || `User ${record.user_id || record.follower_id}`;
        email.textContent = user.email || "";
        meta.append(name, email);
        item.appendChild(meta);
        container.appendChild(item);
    });
}

function renderPosts(posts) {
    const postsList = $("#postsList");
    postsList.innerHTML = "";
    postsList.classList.remove("empty");

    if (!state.token) {
        renderEmpty(postsList, "Login to load posts.");
        return;
    }

    if (!posts.length) {
        renderEmpty(postsList, state.postsTab === "feed" ? "Follow writers or publish a post to build your feed." : "You have not published yet.");
        return;
    }

    posts.forEach((post) => {
        const card = itemShell("post");
        const title = document.createElement("h3");
        const content = document.createElement("p");
        const meta = document.createElement("div");
        const author = state.users.find((user) => user.id === post.user_id);

        title.textContent = post.title;
        content.textContent = post.content || "";
        meta.className = "post-meta";
        meta.textContent = `${author ? author.name : `User ${post.user_id}`} - ${post.date_created} - ${post.likes} likes`;

        card.append(title, content, meta);
        postsList.appendChild(card);
    });
}

function addNotice(message) {
    const notices = $("#noticesList");
    if (notices.classList.contains("empty")) {
        notices.innerHTML = "";
        notices.classList.remove("empty");
    }

    const item = itemShell("notice");
    item.textContent = message;
    notices.prepend(item);
}

function connectSocket() {
    if (!state.token) {
        return;
    }

    if (state.socket) {
        state.socket.close();
    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    state.socket = new WebSocket(`${protocol}://${window.location.host}/ws?token=${state.token}`);

    state.socket.addEventListener("open", () => {
        $("#socketState").textContent = "Live";
        $("#socketState").classList.remove("muted");
        addNotice("Connected to live updates.");
    });

    state.socket.addEventListener("message", (event) => {
        let data = event.data;
        try {
            data = JSON.parse(event.data);
        } catch {
            data = {message: event.data};
        }

        if (data.type === "post_created") {
            addNotice(`${data.author} published "${data.title}".`);
            if (state.postsTab === "feed") {
                loadPosts().catch((error) => showToast(error.message || "Could not refresh feed.", true));
            }
            return;
        }

        addNotice(data.message || JSON.stringify(data));
    });

    state.socket.addEventListener("close", () => {
        if (!state.socket || state.socket.readyState === WebSocket.CLOSED) {
            $("#socketState").textContent = "Offline";
            $("#socketState").classList.add("muted");
        }
    });
}

async function loadUsers() {
    if (!state.token) {
        renderUsers();
        return;
    }

    state.users = await request("/users/");
    renderUsers();
}

async function loadRelationships() {
    if (!state.token) {
        state.followings = [];
        state.followers = [];
        renderRelationshipList("#followingList", "#followingCount", [], "No followed writers yet.");
        renderRelationshipList("#followersList", "#followersCount", [], "No followers yet.");
        renderUsers();
        return;
    }

    const [followings, followers] = await Promise.all([
        request("/following/"),
        request("/following/followers"),
    ]);

    state.followings = followings;
    state.followers = followers;
    renderRelationshipList("#followingList", "#followingCount", followings, "No followed writers yet.");
    renderRelationshipList("#followersList", "#followersCount", followers, "No followers yet.");
    renderUsers();
}

async function loadPosts() {
    if (!state.token) {
        renderPosts([]);
        return;
    }

    const path = state.postsTab === "feed" ? "/posts/feed" : "/posts/";
    const posts = await request(path);
    renderPosts(posts);
}

async function refreshApp() {
    setSessionFromToken();

    if (state.token && !state.user) {
        clearSession();
    }

    if (!state.token || !state.user) {
        renderSignedOut();
        return;
    }

    await loadUsers();
    await loadRelationships();
    await loadPosts();
    connectSocket();
}

function renderSignedOut() {
    setSessionFromToken();
    renderUsers();
    renderPosts([]);
    renderRelationshipList("#followingList", "#followingCount", [], "No followed writers yet.");
    renderRelationshipList("#followersList", "#followersCount", [], "No followers yet.");
    renderEmpty($("#noticesList"), "No live notices.");
    $("#socketState").textContent = "Offline";
    $("#socketState").classList.add("muted");
}

async function register(event) {
    event.preventDefault();
    const data = await request("/auth/register", {
        method: "POST",
        body: {
            name: $("#registerName").value.trim(),
            email: $("#registerEmail").value.trim(),
            phone_number: $("#registerPhone").value.trim(),
            password: $("#registerPassword").value,
        },
    });

    $("#registerForm").reset();
    $("#loginEmail").value = data.data.email;
    setAuthTab("login");
    showToast("Account created. Login to continue.");
}

async function login(event) {
    event.preventDefault();
    const body = new URLSearchParams();
    body.append("username", $("#loginEmail").value.trim());
    body.append("password", $("#loginPassword").value);

    const data = await request("/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body,
    });

    state.token = data.access_token;
    localStorage.setItem("token", state.token);
    showToast("Logged in.");
    $("#loginForm").reset();
    await refreshApp();
}

async function createPost(event) {
    event.preventDefault();
    if (!state.token) {
        showToast("Login before publishing.", true);
        return;
    }

    await request("/posts/", {
        method: "POST",
        body: {
            title: $("#postTitle").value.trim(),
            content: $("#postContent").value.trim(),
        },
    });

    $("#postForm").reset();
    showToast("Post published.");
    await loadPosts();
}

async function toggleFollow(userId, isFollowing) {
    const action = isFollowing ? "unfollow" : "follow";
    await request(`/following/${action}/user/${userId}`, {method: "POST"});
    showToast(isFollowing ? "User unfollowed." : "User followed.");
    await loadRelationships();
    await loadPosts();
}

function logout() {
    clearSession();
    showToast("Logged out.");
    renderSignedOut();
}

function bindEvents() {
    $("#loginForm").addEventListener("submit", withErrorHandling(login));
    $("#registerForm").addEventListener("submit", withErrorHandling(register));
    $("#postForm").addEventListener("submit", withErrorHandling(createPost));
    $("#logoutBtn").addEventListener("click", logout);
    $("#refreshUsersBtn").addEventListener("click", withErrorHandling(async () => {
        await loadUsers();
        await loadRelationships();
    }));
    $("#refreshPostsBtn").addEventListener("click", withErrorHandling(loadPosts));
    $("#clearNoticesBtn").addEventListener("click", () => renderEmpty($("#noticesList"), "No live notices."));

    document.querySelectorAll("[data-auth-tab]").forEach((button) => {
        button.addEventListener("click", () => setAuthTab(button.dataset.authTab));
    });

    document.querySelectorAll("[data-post-tab]").forEach((button) => {
        button.addEventListener("click", () => setPostTab(button.dataset.postTab));
    });
}

function withErrorHandling(handler) {
    return async (event) => {
        try {
            await handler(event);
        } catch (error) {
            showToast(error.message || "Something went wrong.", true);
        }
    };
}

document.addEventListener("DOMContentLoaded", () => {
    bindEvents();
    refreshApp().catch((error) => showToast(error.message, true));
});
