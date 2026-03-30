let subscribers = [];
let currentDevices = [];
let currentUsage = null;
let selectedUserId = null;
let selectedDeviceId = null;

let isLoadingSubscribers = false;
let isLoadingDevices = false;
let isLoadingUsage = false;

let subscriberErrorMessage = "";
let deviceErrorMessage = "";
let usageErrorMessage = "";

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

function createBadge(value) {
    const badge = document.createElement("span");
    badge.className = badgeClass(value);
    badge.textContent = value || "-";
    return badge;
}

function createStatusCell(status) {
    const cell = document.createElement("td");
    cell.appendChild(createBadge(status));
    return cell;
}

function getSelectedSubscriber() {
    return subscribers.find((subscriber) => subscriber.userId === selectedUserId) || null;
}

function getSelectedDevice() {
    return currentDevices.find((device) => device.deviceId === selectedDeviceId) || null;
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
        row.classList.add("clickable");

        if (subscriber.userId === selectedUserId) {
            row.classList.add("selected");
        }

        row.addEventListener("click", () => {
            selectSubscriber(subscriber.userId);
        });

        row.appendChild(createCell(subscriber.userId || "-"));
        row.appendChild(createCell(subscriber.name || "-"));
        row.appendChild(createCell(subscriber.plan || "-"));
        row.appendChild(createStatusCell(subscriber.status));
        row.appendChild(createCell(String(subscriber.deviceCount ?? "-")));

        tbody.appendChild(row);
    });
}

async function selectSubscriber(userId) {
    selectedUserId = userId;
    selectedDeviceId = null;
    currentDevices = [];
    currentUsage = null;
    deviceErrorMessage = "";
    usageErrorMessage = "";
    isLoadingDevices = true;
    isLoadingUsage = false;

    renderSubscribers();
    renderDevices();
    renderUsage();

    try {
        const res = await fetch(`/api/subscribers/${encodeURIComponent(userId)}/devices`);

        if (!res.ok) {
            throw new Error(`Failed to fetch devices: ${res.status}`);
        }

        const data = await res.json();

        if (!Array.isArray(data)) {
            throw new Error("Devices response must be an array.");
        }

        currentDevices = data;
    } catch (error) {
        currentDevices = [];
        deviceErrorMessage = "Failed to load devices for the selected subscriber.";
        console.error(error);
    } finally {
        isLoadingDevices = false;
        renderDevices();
        renderUsage();
    }
}

function renderDevices() {
    const tableEl = document.getElementById("device-table");
    const tbody = document.getElementById("device-body");
    const emptyEl = document.getElementById("device-empty");
    const summaryEl = document.getElementById("device-summary");
    const searchInput = document.getElementById("device-search");
    const statusFilterInput = document.getElementById("device-status-filter");
    const selectedSubscriber = getSelectedSubscriber();

    if (!tableEl || !tbody || !emptyEl || !summaryEl || !searchInput || !statusFilterInput) {
        return;
    }

    const search = searchInput.value.trim().toLowerCase();
    const statusFilter = statusFilterInput.value.toLowerCase();

    tbody.replaceChildren();

    if (!selectedSubscriber) {
        summaryEl.textContent = "Select a subscriber to view registered devices.";
        emptyEl.textContent = "Select a subscriber to view registered devices.";
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        return;
    }

    if (isLoadingDevices) {
        summaryEl.textContent = `Loading devices for ${selectedSubscriber.name} (${selectedSubscriber.userId})...`;
        emptyEl.textContent = "Loading devices...";
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        return;
    }

    if (deviceErrorMessage) {
        summaryEl.textContent = `0 devices for ${selectedSubscriber.name} (${selectedSubscriber.userId})`;
        emptyEl.textContent = deviceErrorMessage;
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        return;
    }

    const filteredDevices = currentDevices.filter((device) => {
        const searchableValues = [
            device.deviceId,
            device.type,
            device.model,
            device.location,
            device.status,
        ];

        const matchesSearch =
            search === "" ||
            searchableValues.some((value) =>
                String(value || "").toLowerCase().includes(search),
            );

        const matchesStatus =
            statusFilter === "" ||
            String(device.status || "").toLowerCase() === statusFilter;

        return matchesSearch && matchesStatus;
    });

    summaryEl.textContent =
        `Showing ${filteredDevices.length} of ${currentDevices.length} devices for ` +
        `${selectedSubscriber.name} (${selectedSubscriber.userId})`;

    if (currentDevices.length === 0) {
        emptyEl.textContent = "No registered devices for this subscriber.";
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        return;
    }

    if (filteredDevices.length === 0) {
        emptyEl.textContent = "No devices matched your search or filter.";
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        return;
    }

    emptyEl.classList.add("hidden");
    tableEl.classList.remove("hidden");

    filteredDevices.forEach((device) => {
        const row = document.createElement("tr");
        row.classList.add("clickable");

        if (device.deviceId === selectedDeviceId) {
            row.classList.add("selected");
        }

        row.addEventListener("click", () => {
            selectDevice(device.deviceId);
        });

        row.appendChild(createCell(device.deviceId || "-"));
        row.appendChild(createCell(device.type || "-"));
        row.appendChild(createCell(device.model || "-"));
        row.appendChild(createCell(device.location || "-"));
        row.appendChild(createStatusCell(device.status));

        tbody.appendChild(row);
    });
}

function createDetailCard(label, value) {
    const card = document.createElement("div");
    const labelEl = document.createElement("span");
    const valueEl = document.createElement("div");

    card.className = "detail-card";
    labelEl.className = "detail-label";
    valueEl.className = "detail-value";

    labelEl.textContent = label;

    if (value instanceof Node) {
        valueEl.appendChild(value);
    } else {
        valueEl.textContent = value;
    }

    card.appendChild(labelEl);
    card.appendChild(valueEl);

    return card;
}

async function selectDevice(deviceId) {
    selectedDeviceId = deviceId;
    currentUsage = null;
    usageErrorMessage = "";
    isLoadingUsage = true;

    renderDevices();
    renderUsage();

    try {
        const res = await fetch(`/api/devices/${encodeURIComponent(deviceId)}/usage`);

        if (!res.ok) {
            throw new Error(`Failed to fetch usage: ${res.status}`);
        }

        const data = await res.json();

        if (!data || Array.isArray(data)) {
            throw new Error("Usage response must be an object.");
        }

        currentUsage = data;
    } catch (error) {
        currentUsage = null;
        usageErrorMessage = "Failed to load usage details for the selected device.";
        console.error(error);
    } finally {
        isLoadingUsage = false;
        renderUsage();
    }
}

function renderUsageChart(trend) {
    const chartEl = document.getElementById("usage-chart");
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

    if (!chartEl) {
        return;
    }

    chartEl.replaceChildren();

    const values = Array.isArray(trend) ? trend : [];
    const maxValue = Math.max(...values, 1);

    days.forEach((day, index) => {
        const value = Number(values[index] ?? 0);
        const column = document.createElement("div");
        const valueLabel = document.createElement("span");
        const barWrap = document.createElement("div");
        const bar = document.createElement("div");
        const dayLabel = document.createElement("span");

        column.className = "chart-column";
        valueLabel.className = "chart-value";
        barWrap.className = "chart-bar-wrap";
        bar.className = "chart-bar";
        dayLabel.className = "chart-day";

        valueLabel.textContent = String(value);
        bar.style.height = `${Math.max((value / maxValue) * 100, value > 0 ? 12 : 6)}%`;
        dayLabel.textContent = day;

        barWrap.appendChild(bar);
        column.appendChild(valueLabel);
        column.appendChild(barWrap);
        column.appendChild(dayLabel);
        chartEl.appendChild(column);
    });
}

function renderUsage() {
    const emptyEl = document.getElementById("usage-empty");
    const detailEl = document.getElementById("usage-detail");
    const infoEl = document.getElementById("usage-info");
    const summaryEl = document.getElementById("usage-summary");
    const selectedSubscriber = getSelectedSubscriber();
    const selectedDevice = getSelectedDevice();

    if (!emptyEl || !detailEl || !infoEl || !summaryEl) {
        return;
    }

    infoEl.replaceChildren();

    if (!selectedSubscriber) {
        summaryEl.textContent = "Select a subscriber first, then choose a device.";
        emptyEl.textContent = "Select a subscriber first, then choose a device.";
        emptyEl.classList.remove("hidden");
        detailEl.classList.add("hidden");
        return;
    }

    if (!selectedDeviceId || !selectedDevice) {
        summaryEl.textContent = "Select a device to view usage details and the weekly trend.";
        emptyEl.textContent = "Select a device to view usage details and the weekly trend.";
        emptyEl.classList.remove("hidden");
        detailEl.classList.add("hidden");
        return;
    }

    if (isLoadingUsage) {
        summaryEl.textContent = `Loading usage details for ${selectedDevice.model} (${selectedDevice.deviceId})...`;
        emptyEl.textContent = "Loading usage details...";
        emptyEl.classList.remove("hidden");
        detailEl.classList.add("hidden");
        return;
    }

    if (usageErrorMessage) {
        summaryEl.textContent = `Usage detail unavailable for ${selectedDevice.model} (${selectedDevice.deviceId})`;
        emptyEl.textContent = usageErrorMessage;
        emptyEl.classList.remove("hidden");
        detailEl.classList.add("hidden");
        return;
    }

    if (!currentUsage) {
        summaryEl.textContent = "Select a device to view usage details and the weekly trend.";
        emptyEl.textContent = "Select a device to view usage details and the weekly trend.";
        emptyEl.classList.remove("hidden");
        detailEl.classList.add("hidden");
        return;
    }

    summaryEl.textContent = `Viewing usage for ${currentUsage.deviceName} (${currentUsage.deviceId})`;
    emptyEl.classList.add("hidden");
    detailEl.classList.remove("hidden");

    const detailCards = [
        createDetailCard("Device ID", currentUsage.deviceId || "-"),
        createDetailCard("Device Name", currentUsage.deviceName || "-"),
        createDetailCard("Power Status", createBadge(currentUsage.powerStatus)),
        createDetailCard("Last Used", currentUsage.lastUsedAt || "-"),
        createDetailCard("Total Usage", `${currentUsage.totalUsageHours ?? 0} hrs`),
        createDetailCard("Weekly Count", String(currentUsage.weeklyUsageCount ?? 0)),
        createDetailCard("Health Status", createBadge(currentUsage.healthStatus)),
        createDetailCard("Remark", currentUsage.remark || "-"),
    ];

    infoEl.append(...detailCards);
    renderUsageChart(currentUsage.weeklyUsageTrend);
}

function bindEvents() {
    const searchInput = document.getElementById("subscriber-search");
    const statusFilterInput = document.getElementById("subscriber-status-filter");
    const deviceSearchInput = document.getElementById("device-search");
    const deviceStatusFilterInput = document.getElementById("device-status-filter");

    if (searchInput) {
        searchInput.addEventListener("input", renderSubscribers);
    }

    if (statusFilterInput) {
        statusFilterInput.addEventListener("change", renderSubscribers);
    }

    if (deviceSearchInput) {
        deviceSearchInput.addEventListener("input", renderDevices);
    }

    if (deviceStatusFilterInput) {
        deviceStatusFilterInput.addEventListener("change", renderDevices);
    }
}

bindEvents();
renderDevices();
renderUsage();
fetchSubscribers();
