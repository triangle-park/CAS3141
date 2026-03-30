let subscribers = [];
let isLoadingSubscribers = false;
let subscriberErrorMessage = "";

function badgeClass(value) {
    const v = (value || "").toLowerCase();

    if (["active", "online", "normal"].includes(v)) {
        return "badge status-active";
    }

    if (["paused", "standby"].includes(v)) {
        return "badge status-paused";
    }

    if (["expired", "error", "warning"].includes(v)) {
        return "badge status-expired";
    }

    if (v === "offline") {
        return "badge status-offline";
    }

    if (["on", "cleaning"].includes(v)) {
        return "badge status-on";
    }

    if (v === "off") {
        return "badge status-off";
    }

    return "badge";
}

async function fetchSubscribers() {
    isLoadingSubscribers = true;
    subscriberErrorMessage = "";
    renderSubscribers();

    try {
        const res = await fetch("/api/subscribers");

        if (!res.ok) {
            throw new Error(`Failed to fetch subscribers: ${res.status}`);
        }

        const data = await res.json();

        if (!Array.isArray(data)) {
            throw new Error("Subscribers response must be an array.");
        }

        subscribers = data;
    } catch (error) {
        subscribers = [];
        subscriberErrorMessage = "Failed to load subscribers from /api/subscribers.";
        console.error(error);
    } finally {
        isLoadingSubscribers = false;
        renderSubscribers();
    }
}

function createCell(text) {
    const cell = document.createElement("td");
    cell.textContent = text;
    return cell;
}

function createStatusCell(status) {
    const cell = document.createElement("td");
    const badge = document.createElement("span");

    badge.className = badgeClass(status);
    badge.textContent = status || "-";

    cell.appendChild(badge);
    return cell;
}

function renderSubscribers() {
    const tableEl = document.getElementById("subscriber-table");
    const tbody = document.getElementById("subscriber-body");
    const emptyEl = document.getElementById("subscriber-empty");
    const summaryEl = document.getElementById("subscriber-summary");
    const searchInput = document.getElementById("subscriber-search");
    const statusFilterInput = document.getElementById("subscriber-status-filter");

    if (!tableEl || !tbody || !emptyEl || !summaryEl || !searchInput || !statusFilterInput) {
        return;
    }

    const search = searchInput.value.trim().toLowerCase();
    const statusFilter = statusFilterInput.value.toLowerCase();

    tbody.replaceChildren();

    if (isLoadingSubscribers) {
        summaryEl.textContent = "Loading subscribers...";
        emptyEl.textContent = "Loading subscribers...";
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        return;
    }

    if (subscriberErrorMessage) {
        summaryEl.textContent = "0 subscribers";
        emptyEl.textContent = subscriberErrorMessage;
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        return;
    }

    const filteredSubscribers = subscribers.filter((subscriber) => {
        const searchableValues = [
            subscriber.userId,
            subscriber.name,
            subscriber.plan,
            subscriber.status,
        ];

        const matchesSearch =
            search === "" ||
            searchableValues.some((value) =>
                String(value || "").toLowerCase().includes(search),
            );

        const matchesStatus =
            statusFilter === "" ||
            String(subscriber.status || "").toLowerCase() === statusFilter;

        return matchesSearch && matchesStatus;
    });

    summaryEl.textContent = `Showing ${filteredSubscribers.length} of ${subscribers.length} subscribers`;

    if (filteredSubscribers.length === 0) {
        emptyEl.textContent =
            subscribers.length === 0
                ? "No subscriber data available."
                : "No subscribers matched your search or filter.";
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        return;
    }

    emptyEl.classList.add("hidden");
    tableEl.classList.remove("hidden");

    filteredSubscribers.forEach((subscriber) => {
        const row = document.createElement("tr");

        row.appendChild(createCell(subscriber.userId || "-"));
        row.appendChild(createCell(subscriber.name || "-"));
        row.appendChild(createCell(subscriber.plan || "-"));
        row.appendChild(createStatusCell(subscriber.status));
        row.appendChild(createCell(String(subscriber.deviceCount ?? "-")));

        tbody.appendChild(row);
    });
}

function bindEvents() {
    const searchInput = document.getElementById("subscriber-search");
    const statusFilterInput = document.getElementById("subscriber-status-filter");

    if (searchInput) {
        searchInput.addEventListener("input", renderSubscribers);
    }

    if (statusFilterInput) {
        statusFilterInput.addEventListener("change", renderSubscribers);
    }
}

bindEvents();
fetchSubscribers();
