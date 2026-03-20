// ===== MECHANO_APP TYPING ENGINE =====

(function () {
    "use strict";

    // --- Settings (persisted to localStorage) ---
    const defaultSettings = {
        theme: "dark",
        scanlines: true,
        keySound: true,
        errorSound: true,
        comboSound: true,
        particles: true,
        screenShake: true,
    };

    let settings = { ...defaultSettings };

    function loadSettings() {
        try {
            const saved = localStorage.getItem("mechano_settings");
            if (saved) settings = { ...defaultSettings, ...JSON.parse(saved) };
        } catch (_) {}
        applySettings();
    }

    function saveSettings() {
        localStorage.setItem("mechano_settings", JSON.stringify(settings));
    }

    function applySettings() {
        // Theme
        document.documentElement.setAttribute("data-theme", settings.theme);

        // Scanlines
        document.body.classList.toggle("no-scanlines", !settings.scanlines);

        // Sync UI controls
        $$(".theme-btn").forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.theme === settings.theme);
        });
        const setCheckbox = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.checked = val;
        };
        setCheckbox("setting-scanlines", settings.scanlines);
        setCheckbox("setting-key-sound", settings.keySound);
        setCheckbox("setting-error-sound", settings.errorSound);
        setCheckbox("setting-combo-sound", settings.comboSound);
        setCheckbox("setting-particles", settings.particles);
        setCheckbox("setting-screen-shake", settings.screenShake);
    }

    function bindSettings() {
        // Theme buttons
        $$(".theme-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                settings.theme = btn.dataset.theme;
                saveSettings();
                applySettings();
            });
        });

        // Toggle checkboxes
        const bindToggle = (id, key) => {
            const el = document.getElementById(id);
            if (el) el.addEventListener("change", () => {
                settings[key] = el.checked;
                saveSettings();
                applySettings();
            });
        };
        bindToggle("setting-scanlines", "scanlines");
        bindToggle("setting-key-sound", "keySound");
        bindToggle("setting-error-sound", "errorSound");
        bindToggle("setting-combo-sound", "comboSound");
        bindToggle("setting-particles", "particles");
        bindToggle("setting-screen-shake", "screenShake");
    }

    // --- Audio Context for sound effects ---
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    function getAudioCtx() {
        if (!audioCtx) audioCtx = new AudioCtx();
        return audioCtx;
    }

    function playKeySound() {
        if (!settings.keySound) return;
        try {
            const ctx = getAudioCtx();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = "square";
            osc.frequency.setValueAtTime(800 + Math.random() * 400, ctx.currentTime);
            gain.gain.setValueAtTime(0.03, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.05);
        } catch (_) {}
    }

    function playErrorSound() {
        if (!settings.errorSound) return;
        try {
            const ctx = getAudioCtx();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = "sawtooth";
            osc.frequency.setValueAtTime(200, ctx.currentTime);
            gain.gain.setValueAtTime(0.06, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.12);
        } catch (_) {}
    }

    function playComboSound() {
        if (!settings.comboSound) return;
        try {
            const ctx = getAudioCtx();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = "sine";
            osc.frequency.setValueAtTime(600, ctx.currentTime);
            osc.frequency.linearRampToValueAtTime(1200, ctx.currentTime + 0.1);
            gain.gain.setValueAtTime(0.05, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.15);
        } catch (_) {}
    }

    function playFinishSound() {
        try {
            const ctx = getAudioCtx();
            [523, 659, 784].forEach((freq, i) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.type = "sine";
                osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.12);
                gain.gain.setValueAtTime(0.05, ctx.currentTime + i * 0.12);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 0.3);
                osc.start(ctx.currentTime + i * 0.12);
                osc.stop(ctx.currentTime + i * 0.12 + 0.3);
            });
        } catch (_) {}
    }

    // --- Visual effects ---
    function spawnParticle(char, x, y, isCorrect) {
        if (!settings.particles) return;
        const el = document.createElement("div");
        el.className = "keystroke-particle";
        el.textContent = char;
        el.style.left = x + "px";
        el.style.top = y + "px";
        el.style.color = isCorrect ? "var(--green)" : "var(--red)";
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 600);
    }

    function spawnComboFlash(streak, x, y) {
        const el = document.createElement("div");
        el.className = "combo-flash";
        el.textContent = streak + "x";
        el.style.left = x + "px";
        el.style.top = (y - 30) + "px";
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 800);
    }

    // --- DOM refs ---
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const textDisplay = $("#text-display");
    const hiddenInput = $("#hidden-input");
    const typingContainer = $("#typing-container");
    const clickHint = $("#click-hint");
    const timerBarFill = $("#timer-bar-fill");
    const timerText = $("#timer-text");
    const resultsOverlay = $("#results-overlay");
    const passageOverlay = $("#passage-select-overlay");
    const passageList = $("#passage-list");
    const codeOverlay = $("#code-select-overlay");
    const codeSnippetList = $("#code-snippet-list");
    const customOverlay = $("#custom-text-overlay");
    const customTextInput = $("#custom-text-input");

    // --- Char error buffer (sent to backend on finish) ---
    let charErrorBuffer = [];

    function recordCharError(expected, typed) {
        charErrorBuffer.push({ expected, typed });
    }

    async function flushCharErrors(resultId) {
        if (charErrorBuffer.length === 0) return;
        const errors = charErrorBuffer.splice(0);
        try {
            await fetch("/api/char-errors", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ errors, result_id: resultId }),
            });
        } catch (_) {}
    }

    // --- State ---
    let state = {
        mode: "words",
        duration: 60,
        text: "",
        chars: [],
        currentIndex: 0,
        errors: 0,
        correctChars: 0,
        totalTyped: 0,
        streak: 0,
        bestStreak: 0,
        started: false,
        finished: false,
        startTime: null,
        timerInterval: null,
        timeLeft: 60,
        previousBestWpm: 0,
        previousBestStreak: 0,
    };

    // --- Lesson State ---
    let lesson = {
        active: false,
        id: null,
        passAccuracy: 90,
        nextId: null,
        text: "",
        chars: [],
        currentIndex: 0,
        errors: 0,
        correctChars: 0,
        totalTyped: 0,
        streak: 0,
        bestStreak: 0,
        started: false,
        finished: false,
        startTime: null,
        levelsData: null,
    };

    // --- Init ---
    async function init() {
        loadSettings();
        await loadPreviousBests();
        await loadText();
        bindEvents();
        bindSettings();
        updateTimerDisplay();
    }

    async function loadPreviousBests() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            state.previousBestWpm = data.best_wpm || 0;
            state.previousBestStreak = data.best_streak || 0;
        } catch (_) {}
    }

    async function loadText() {
        if (state.mode === "words" || state.mode === "sudden_death") {
            const res = await fetch("/api/words?count=250");
            const data = await res.json();
            state.text = data.words;
        } else if (state.mode === "code") {
            // Text set via showCodeSelector -> loadCodeSnippet
            return;
        } else if (state.mode === "custom") {
            // Text set via custom text overlay
            return;
        }
        renderText();
    }

    async function loadPassage(index) {
        const res = await fetch(`/api/passage?index=${index}`);
        const data = await res.json();
        state.text = data.text;
        renderText();
        passageOverlay.classList.remove("active");
    }

    async function showPassageSelector() {
        const res = await fetch("/api/passages");
        const data = await res.json();
        passageList.innerHTML = "";
        data.passages.forEach((p, i) => {
            const el = document.createElement("div");
            el.className = "passage-option";
            el.innerHTML = `
                <div class="passage-option-title">${p.title}</div>
                <div class="passage-option-preview">${p.text.substring(0, 80)}...</div>
            `;
            el.addEventListener("click", () => loadPassage(i));
            passageList.appendChild(el);
        });
        passageOverlay.classList.add("active");
    }

    async function showCodeSelector() {
        const res = await fetch("/api/code-snippets");
        const data = await res.json();
        codeSnippetList.innerHTML = "";
        data.snippets.forEach((s, i) => {
            const el = document.createElement("div");
            el.className = "passage-option";
            el.innerHTML = `
                <div class="passage-option-title">${escapeHtml(s.title)}</div>
                <div class="passage-option-preview">${escapeHtml(s.text.substring(0, 80))}...</div>
            `;
            el.addEventListener("click", () => loadCodeSnippet(i));
            codeSnippetList.appendChild(el);
        });
        codeOverlay.classList.add("active");
    }

    async function loadCodeSnippet(index) {
        const res = await fetch(`/api/code-snippet?index=${index}`);
        const data = await res.json();
        state.text = data.text;
        codeOverlay.classList.remove("active");
        renderText();
    }

    function showCustomTextOverlay() {
        customTextInput.value = "";
        customOverlay.classList.add("active");
        customTextInput.focus();
    }

    function startCustomText() {
        const text = customTextInput.value.trim();
        if (!text) return;
        // Normalize whitespace: collapse runs of whitespace into single spaces
        state.text = text.replace(/\s+/g, " ");
        customOverlay.classList.remove("active");
        renderText();
    }

    function renderTextToDisplay(text, displayEl, inputEl, hintEl) {
        const words = text.split(" ");
        let html = "";
        let charIdx = 0;
        words.forEach((word, wi) => {
            html += '<span class="word">';
            for (let j = 0; j < word.length; j++) {
                const c = escapeHtml(word[j]);
                const cls = charIdx === 0 ? "char current" : "char upcoming";
                html += `<span class="${cls}" data-index="${charIdx}">${c}</span>`;
                charIdx++;
            }
            html += '</span>';
            if (wi < words.length - 1) {
                const cls = charIdx === 0 ? "char current" : "char upcoming";
                html += `<span class="${cls}" data-index="${charIdx}">&nbsp;</span>`;
                charIdx++;
            }
        });
        displayEl.innerHTML = html;
        inputEl.value = "";
        displayEl.style.transform = "translateY(0)";
        hintEl.style.display = "";
        hintEl.style.opacity = "1";
    }

    function renderText() {
        state.chars = state.text.split("");
        state.currentIndex = 0;
        state.errors = 0;
        state.correctChars = 0;
        state.totalTyped = 0;
        state.streak = 0;
        state.bestStreak = 0;
        state.started = false;
        state.finished = false;
        state.startTime = null;
        clearInterval(state.timerInterval);
        state.timeLeft = state.duration;

        renderTextToDisplay(state.text, textDisplay, hiddenInput, clickHint);
        updateLiveStats();
        updateTimerDisplay();
        timerBarFill.style.width = "100%";
        timerBarFill.className = "timer-bar-fill";
        timerText.className = "timer-text";
    }

    function escapeHtml(str) {
        const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
        return str.replace(/[&<>"']/g, (m) => map[m]);
    }

    // --- Typing logic ---
    function handleInput(e) {
        if (state.finished) return;

        const inputVal = hiddenInput.value;
        if (inputVal.length === 0) return;

        // Take only the last character typed
        const typedChar = inputVal[inputVal.length - 1];
        hiddenInput.value = "";

        if (!state.started) {
            state.started = true;
            state.startTime = Date.now();
            clickHint.style.display = "none";
            startTimer();
        }

        const expected = state.chars[state.currentIndex];
        const charSpan = textDisplay.querySelector(`[data-index="${state.currentIndex}"]`);
        const rect = charSpan ? charSpan.getBoundingClientRect() : null;

        state.totalTyped++;

        if (typedChar === expected) {
            charSpan.classList.remove("current", "upcoming");
            charSpan.classList.add("correct");
            state.correctChars++;
            state.streak++;
            if (state.streak > state.bestStreak) state.bestStreak = state.streak;

            playKeySound();
            if (rect) spawnParticle(typedChar, rect.left + rect.width / 2, rect.top, true);

            // Combo milestones
            if (state.streak > 0 && state.streak % 10 === 0) {
                playComboSound();
                if (rect) spawnComboFlash(state.streak, rect.left, rect.top);
            }
        } else {
            charSpan.classList.remove("current", "upcoming");
            charSpan.classList.add("incorrect");
            state.errors++;
            state.streak = 0;
            recordCharError(expected, typedChar);

            playErrorSound();
            if (rect) spawnParticle(typedChar, rect.left + rect.width / 2, rect.top, false);
            typingContainer.classList.add("error-flash");
            if (settings.screenShake) typingContainer.classList.add("screen-shake");
            setTimeout(() => typingContainer.classList.remove("error-flash", "screen-shake"), 150);

            // Sudden death: one mistake = game over
            if (state.mode === "sudden_death") {
                state.currentIndex++;
                updateLiveStats();
                finishTest();
                return;
            }
        }

        state.currentIndex++;

        // Mark next char as current
        if (state.currentIndex < state.chars.length) {
            const next = textDisplay.querySelector(`[data-index="${state.currentIndex}"]`);
            if (next) {
                next.classList.remove("upcoming");
                next.classList.add("current");
            }

            // Auto-scroll: shift text up so current line stays visible
            if (next) {
                const lineHeight = parseFloat(getComputedStyle(textDisplay).lineHeight);
                const firstCharTop = textDisplay.querySelector('[data-index="0"]')?.offsetTop || 0;
                const currentTop = next.offsetTop;
                const linesScrolled = Math.floor((currentTop - firstCharTop) / lineHeight);
                // Start shifting after the first line
                if (linesScrolled > 0) {
                    textDisplay.style.transform = `translateY(-${linesScrolled * lineHeight}px)`;
                }
            }
        } else {
            finishTest();
        }

        updateLiveStats();
    }

    // --- Timer ---
    function startTimer() {
        state.timerInterval = setInterval(() => {
            state.timeLeft--;
            updateTimerDisplay();

            const pct = (state.timeLeft / state.duration) * 100;
            timerBarFill.style.width = pct + "%";

            if (pct <= 20) {
                timerBarFill.className = "timer-bar-fill danger";
                timerText.className = "timer-text danger";
            } else if (pct <= 40) {
                timerBarFill.className = "timer-bar-fill warning";
                timerText.className = "timer-text warning";
            }

            if (state.timeLeft <= 0) {
                finishTest();
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        timerText.textContent = state.timeLeft;
    }

    // --- Stats ---
    function calcWpm() {
        if (!state.startTime) return 0;
        const elapsed = (Date.now() - state.startTime) / 1000 / 60;
        if (elapsed === 0) return 0;
        return Math.round((state.correctChars / 5) / elapsed);
    }

    function calcAccuracy() {
        if (state.totalTyped === 0) return 100;
        return Math.round((state.correctChars / state.totalTyped) * 100);
    }

    function updateLiveStats() {
        $("#live-wpm").textContent = calcWpm();
        $("#live-accuracy").textContent = calcAccuracy();
        $("#live-errors").textContent = state.errors;
        $("#live-streak").textContent = state.streak;
    }

    // --- Finish ---
    async function finishTest() {
        if (state.finished) return;
        state.finished = true;
        clearInterval(state.timerInterval);
        hiddenInput.blur();

        const wpm = calcWpm();
        const accuracy = calcAccuracy();

        playFinishSound();

        // Show results
        $("#result-wpm").textContent = wpm;
        $("#result-accuracy").textContent = accuracy;
        $("#result-errors").textContent = state.errors;
        $("#result-streak").textContent = state.bestStreak;

        // New best badges
        if (wpm > state.previousBestWpm && state.previousBestWpm > 0) {
            $("#badge-wpm").style.display = "inline-block";
        } else {
            $("#badge-wpm").style.display = "none";
        }
        if (state.bestStreak > state.previousBestStreak && state.previousBestStreak > 0) {
            $("#badge-streak").style.display = "inline-block";
        } else {
            $("#badge-streak").style.display = "none";
        }

        resultsOverlay.classList.add("active");

        // Save to backend
        let resultId = null;
        try {
            const res = await fetch("/api/results", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    wpm: wpm,
                    accuracy: accuracy,
                    errors: state.errors,
                    total_chars: state.totalTyped,
                    correct_chars: state.correctChars,
                    streak: state.bestStreak,
                    duration: state.duration,
                    mode: state.mode,
                }),
            });
            const resData = await res.json();
            resultId = resData.id;
        } catch (_) {}

        await flushCharErrors(resultId);
        await loadPreviousBests();
    }

    // --- Restart ---
    async function restart() {
        resultsOverlay.classList.remove("active");
        await loadText();
        hiddenInput.focus();
    }

    // --- Stats View ---
    let statsDuration = 60;
    let statsMode = null;

    function buildStatsQuery() {
        const params = [];
        if (statsDuration) params.push(`duration=${statsDuration}`);
        if (statsMode) params.push(`mode=${statsMode}`);
        return params.length > 0 ? "?" + params.join("&") : "";
    }

    async function loadStats() {
        try {
            const query = buildStatsQuery();
            const res = await fetch(`/api/stats${query}`);
            const data = await res.json();

            $("#stat-total-tests").textContent = data.total_tests;
            $("#stat-avg-wpm").textContent = Math.round(data.avg_wpm);
            $("#stat-best-wpm").textContent = Math.round(data.best_wpm);
            $("#stat-avg-accuracy").textContent = Math.round(data.avg_accuracy);
            $("#stat-best-streak").textContent = data.best_streak;
            $("#stat-total-chars").textContent = data.total_chars_typed.toLocaleString();

            // Charts
            renderChart(data.history);
            renderAccuracyChart(data.history);

            // History table
            const res2 = await fetch(`/api/results?limit=20${query ? "&" + query.slice(1) : ""}`);
            const data2 = await res2.json();
            renderHistory(data2.results);
        } catch (_) {}
    }

    function renderLineChart(svgSelector, history, opts) {
        const svg = $(svgSelector);
        const chartCanvas = svg.closest(".chart-canvas") || $(".chart-canvas");

        const oldTooltip = chartCanvas.querySelector(".chart-tooltip");
        if (oldTooltip) oldTooltip.remove();

        if (!history || history.length === 0) {
            svg.innerHTML = '<text x="50%" y="50%" text-anchor="middle" fill="#484f58" font-family="monospace" font-size="14">no data yet</text>';
            return;
        }

        const data = [...history].reverse();
        const w = svg.clientWidth || 900;
        const h = svg.clientHeight || 200;
        const pad = { top: 20, right: 20, bottom: 30, left: 45 };
        const plotW = w - pad.left - pad.right;
        const plotH = h - pad.top - pad.bottom;

        const values = data.map((d) => d[opts.dataKey]);
        const { min: minVal, max: maxVal } = opts.minMax(values);
        const range = maxVal - minVal || 10;

        const xStep = data.length > 1 ? plotW / (data.length - 1) : plotW / 2;

        const points = data.map((d, i) => ({
            x: pad.left + i * xStep,
            y: pad.top + plotH - ((d[opts.dataKey] - minVal) / range) * plotH,
            wpm: d.wpm,
            accuracy: d.accuracy,
            streak: d.streak,
            date: d.created_at,
        }));

        let pathD = "";
        let areaD = "";
        let dots = "";

        points.forEach((p, i) => {
            if (i === 0) {
                pathD += `M ${p.x} ${p.y}`;
                areaD += `M ${p.x} ${pad.top + plotH} L ${p.x} ${p.y}`;
            } else {
                pathD += ` L ${p.x} ${p.y}`;
                areaD += ` L ${p.x} ${p.y}`;
            }
            dots += `<circle cx="${p.x}" cy="${p.y}" r="3" fill="${opts.dotColor}" opacity="0.8"/>`;
            dots += `<circle cx="${p.x}" cy="${p.y}" r="12" fill="transparent" data-point="${i}" class="chart-hit"/>`;
        });
        areaD += ` L ${points[points.length - 1].x} ${pad.top + plotH} Z`;

        const styles = getComputedStyle(document.documentElement);
        const chartLabelColor = styles.getPropertyValue("--chart-label").trim();
        const chartGridColor = styles.getPropertyValue("--chart-grid").trim();
        const strokeColor = opts.colorVar ? (styles.getPropertyValue(opts.colorVar).trim() || opts.dotColor) : opts.dotColor;

        let yLabels = "";
        for (let i = 0; i <= 4; i++) {
            const val = Math.round(minVal + (range / 4) * i);
            const y = pad.top + plotH - (plotH / 4) * i;
            yLabels += `<text x="${pad.left - 8}" y="${y + 4}" text-anchor="end" fill="${chartLabelColor}" font-size="10" font-family="monospace">${val}${opts.yLabelSuffix}</text>`;
            yLabels += `<line x1="${pad.left}" y1="${y}" x2="${w - pad.right}" y2="${y}" stroke="${chartGridColor}" stroke-width="1"/>`;
        }

        svg.innerHTML = `
            ${yLabels}
            <path d="${areaD}" fill="url(#${opts.gradientId})" opacity="0.3"/>
            <path d="${pathD}" fill="none" stroke="${strokeColor}" stroke-width="2"/>
            ${dots}
            <defs>
                <linearGradient id="${opts.gradientId}" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="${strokeColor}" stop-opacity="0.4"/>
                    <stop offset="100%" stop-color="${strokeColor}" stop-opacity="0"/>
                </linearGradient>
            </defs>
        `;

        const tooltip = document.createElement("div");
        tooltip.className = "chart-tooltip";
        chartCanvas.appendChild(tooltip);

        svg.querySelectorAll(".chart-hit").forEach((circle) => {
            circle.addEventListener("mouseenter", () => {
                const idx = parseInt(circle.dataset.point);
                const p = points[idx];
                const dateStr = p.date ? new Date(p.date + "Z").toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "";
                tooltip.innerHTML = opts.tooltipHtml(p, dateStr);
                const canvasRect = chartCanvas.getBoundingClientRect();
                const svgRect = svg.getBoundingClientRect();
                let left = svgRect.left - canvasRect.left + p.x - tooltip.offsetWidth / 2;
                let top = svgRect.top - canvasRect.top + p.y - tooltip.offsetHeight - 12;
                left = Math.max(0, Math.min(left, canvasRect.width - tooltip.offsetWidth));
                if (top < 0) top = svgRect.top - canvasRect.top + p.y + 16;
                tooltip.style.left = left + "px";
                tooltip.style.top = top + "px";
                tooltip.classList.add("visible");
            });
            circle.addEventListener("mouseleave", () => {
                tooltip.classList.remove("visible");
            });
        });
    }

    function renderChart(history) {
        renderLineChart("#chart-wpm", history, {
            dataKey: "wpm",
            dotColor: "#58a6ff",
            colorVar: "--accent",
            gradientId: "area-gradient",
            yLabelSuffix: "",
            minMax: (values) => ({
                min: Math.min(...values, 0),
                max: Math.max(...values, 10),
            }),
            tooltipHtml: (p, dateStr) => `
                <div class="chart-tooltip-wpm">${Math.round(p.wpm)} WPM</div>
                <div class="chart-tooltip-acc">${Math.round(p.accuracy)}% accuracy</div>
                <div class="chart-tooltip-date">${dateStr}</div>
            `,
        });
    }

    function renderAccuracyChart(history) {
        renderLineChart("#chart-accuracy", history, {
            dataKey: "accuracy",
            dotColor: "#3fb950",
            colorVar: "--green",
            gradientId: "acc-area-gradient",
            yLabelSuffix: "%",
            minMax: (values) => ({
                min: Math.max(Math.min(...values) - 5, 0),
                max: Math.min(Math.max(...values, 10) + 2, 100),
            }),
            tooltipHtml: (p, dateStr) => `
                <div class="chart-tooltip-wpm">${Math.round(p.accuracy)}% accuracy</div>
                <div class="chart-tooltip-acc">${Math.round(p.wpm)} WPM</div>
                <div class="chart-tooltip-date">${dateStr}</div>
            `,
        });
    }

    function renderHistory(results) {
        const tbody = $("#history-body");
        const empty = $("#empty-state");

        if (!results || results.length === 0) {
            tbody.innerHTML = "";
            empty.style.display = "block";
            return;
        }

        empty.style.display = "none";
        tbody.innerHTML = results
            .map(
                (r, i) => `
            <tr>
                <td style="color: var(--text-muted)">${results.length - i}</td>
                <td style="color: var(--accent)">${Math.round(r.wpm)}</td>
                <td style="color: var(--green)">${Math.round(r.accuracy)}%</td>
                <td style="color: var(--yellow)">${r.streak}</td>
                <td style="color: var(--text-secondary)">${r.mode}</td>
                <td style="color: var(--text-muted)">${r.duration}s</td>
            </tr>
        `
            )
            .join("");
    }

    // ===== LESSON SYSTEM =====

    const lessonBrowser = $("#lesson-browser");
    const lessonActiveEl = $("#lesson-active");
    const lessonTextDisplay = $("#lesson-text-display");
    const lessonHiddenInput = $("#lesson-hidden-input");
    const lessonTypingContainer = $("#lesson-typing-container");
    const lessonClickHint = $("#lesson-click-hint");
    const lessonResultsOverlay = $("#lesson-results-overlay");

    async function loadLessons() {
        try {
            const res = await fetch("/api/lessons");
            const data = await res.json();
            lesson.levelsData = data.levels;
            renderLessonBrowser(data.levels);
        } catch (_) {}
    }

    function renderLessonBrowser(levels) {
        const container = $("#lesson-levels");
        let totalLessons = 0;
        let completedLessons = 0;

        levels.forEach((lvl) => {
            lvl.lessons.forEach((l) => {
                totalLessons++;
                if (l.status === "completed") completedLessons++;
            });
        });

        $("#learn-progress-summary").textContent = `${completedLessons}/${totalLessons} completed`;

        container.innerHTML = levels.map((lvl) => {
            const done = lvl.lessons.filter((l) => l.status === "completed").length;
            const pct = Math.round((done / lvl.lessons.length) * 100);
            return `
                <div class="level-group">
                    <div class="level-header" data-level="${lvl.level}">
                        <div class="level-number">${lvl.level}</div>
                        <div class="level-name">${lvl.level_name}</div>
                        <div class="level-progress">${done}/${lvl.lessons.length}</div>
                        <div class="level-progress-bar">
                            <div class="level-progress-fill" style="width:${pct}%"></div>
                        </div>
                    </div>
                    <div class="level-lessons" data-level-lessons="${lvl.level}">
                        ${lvl.lessons.map((l) => renderLessonCard(l)).join("")}
                    </div>
                </div>
            `;
        }).join("");

        // Bind level toggle
        container.querySelectorAll(".level-header").forEach((hdr) => {
            hdr.addEventListener("click", () => {
                const lessons = container.querySelector(`[data-level-lessons="${hdr.dataset.level}"]`);
                lessons.classList.toggle("collapsed");
            });
        });

        // Bind lesson card clicks
        container.querySelectorAll(".lesson-card[data-lesson-id]").forEach((card) => {
            if (card.classList.contains("locked")) return;
            card.addEventListener("click", () => startLesson(card.dataset.lessonId));
        });
    }

    function renderLessonCard(l) {
        let icon = "";
        if (l.status === "completed") icon = "&#10003;";
        else if (l.status === "available") icon = "&#9654;";
        else icon = "&#128274;";

        const keys = l.keys.length > 0
            ? `<div class="lesson-card-keys">${l.keys.map((k) => `<span class="key-tag">${escapeHtml(k)}</span>`).join("")}</div>`
            : "";

        const stats = l.best_wpm !== undefined
            ? `<div class="lesson-card-stats">
                   <div class="lesson-card-stats-wpm">${Math.round(l.best_wpm)} wpm</div>
                   <div class="lesson-card-stats-acc">${Math.round(l.best_accuracy)}%</div>
               </div>`
            : "";

        return `
            <div class="lesson-card ${l.status}" data-lesson-id="${l.status !== "locked" ? l.id : ""}">
                <div class="lesson-status-icon ${l.status}">${icon}</div>
                <div class="lesson-info">
                    <div class="lesson-card-title">${l.title}</div>
                    <div class="lesson-card-desc">${l.description}</div>
                </div>
                ${keys}
                ${stats}
            </div>
        `;
    }

    async function startLesson(lessonId) {
        try {
            const res = await fetch(`/api/lesson/${lessonId}`);
            const data = await res.json();

            lesson.active = true;
            lesson.id = lessonId;
            lesson.passAccuracy = data.pass_accuracy;
            lesson.text = data.text;
            lesson.chars = data.text.split("");
            lesson.currentIndex = 0;
            lesson.errors = 0;
            lesson.correctChars = 0;
            lesson.totalTyped = 0;
            lesson.streak = 0;
            lesson.bestStreak = 0;
            lesson.started = false;
            lesson.finished = false;
            lesson.startTime = null;

            // Find next lesson ID
            lesson.nextId = null;
            if (lesson.levelsData) {
                const allIds = [];
                lesson.levelsData.forEach((lvl) => lvl.lessons.forEach((l) => allIds.push(l.id)));
                const idx = allIds.indexOf(lessonId);
                if (idx >= 0 && idx < allIds.length - 1) lesson.nextId = allIds[idx + 1];
            }

            // Update header
            $("#lesson-active-title").textContent = data.title;
            const keysEl = $("#lesson-active-keys");
            keysEl.innerHTML = data.keys.length > 0
                ? data.keys.map((k) => `<span class="key-tag">${escapeHtml(k)}</span>`).join("")
                : "";
            $("#lesson-active-target").textContent = `${data.pass_accuracy}% to pass`;

            // Render text
            renderLessonText();

            // Show active view
            lessonBrowser.style.display = "none";
            lessonActiveEl.style.display = "block";
            lessonHiddenInput.focus();
        } catch (_) {}
    }

    function renderLessonText() {
        renderTextToDisplay(lesson.text, lessonTextDisplay, lessonHiddenInput, lessonClickHint);
        updateLessonLiveStats();
    }

    function handleLessonInput() {
        if (lesson.finished) return;

        const inputVal = lessonHiddenInput.value;
        if (inputVal.length === 0) return;

        const typedChar = inputVal[inputVal.length - 1];
        lessonHiddenInput.value = "";

        if (!lesson.started) {
            lesson.started = true;
            lesson.startTime = Date.now();
            lessonClickHint.style.display = "none";
        }

        const expected = lesson.chars[lesson.currentIndex];
        const charSpan = lessonTextDisplay.querySelector(`[data-index="${lesson.currentIndex}"]`);
        const rect = charSpan ? charSpan.getBoundingClientRect() : null;

        lesson.totalTyped++;

        if (typedChar === expected) {
            charSpan.classList.remove("current", "upcoming");
            charSpan.classList.add("correct");
            lesson.correctChars++;
            lesson.streak++;
            if (lesson.streak > lesson.bestStreak) lesson.bestStreak = lesson.streak;

            playKeySound();
            if (rect) spawnParticle(typedChar, rect.left + rect.width / 2, rect.top, true);

            if (lesson.streak > 0 && lesson.streak % 10 === 0) {
                playComboSound();
                if (rect) spawnComboFlash(lesson.streak, rect.left, rect.top);
            }
        } else {
            charSpan.classList.remove("current", "upcoming");
            charSpan.classList.add("incorrect");
            lesson.errors++;
            lesson.streak = 0;
            recordCharError(expected, typedChar);

            playErrorSound();
            if (rect) spawnParticle(typedChar, rect.left + rect.width / 2, rect.top, false);
            lessonTypingContainer.classList.add("error-flash");
            if (settings.screenShake) lessonTypingContainer.classList.add("screen-shake");
            setTimeout(() => lessonTypingContainer.classList.remove("error-flash", "screen-shake"), 150);
        }

        lesson.currentIndex++;

        if (lesson.currentIndex < lesson.chars.length) {
            const next = lessonTextDisplay.querySelector(`[data-index="${lesson.currentIndex}"]`);
            if (next) {
                next.classList.remove("upcoming");
                next.classList.add("current");
                const lineHeight = parseFloat(getComputedStyle(lessonTextDisplay).lineHeight);
                const firstCharTop = lessonTextDisplay.querySelector('[data-index="0"]')?.offsetTop || 0;
                const currentTop = next.offsetTop;
                const linesScrolled = Math.floor((currentTop - firstCharTop) / lineHeight);
                if (linesScrolled > 0) {
                    lessonTextDisplay.style.transform = `translateY(-${linesScrolled * lineHeight}px)`;
                }
            }
        } else {
            finishLesson();
        }

        updateLessonLiveStats();
    }

    function calcLessonWpm() {
        if (!lesson.startTime) return 0;
        const elapsed = (Date.now() - lesson.startTime) / 1000 / 60;
        if (elapsed === 0) return 0;
        return Math.round((lesson.correctChars / 5) / elapsed);
    }

    function calcLessonAccuracy() {
        if (lesson.totalTyped === 0) return 100;
        return Math.round((lesson.correctChars / lesson.totalTyped) * 100);
    }

    function updateLessonLiveStats() {
        $("#lesson-live-wpm").textContent = calcLessonWpm();
        $("#lesson-live-accuracy").textContent = calcLessonAccuracy();
        $("#lesson-live-errors").textContent = lesson.errors;
        $("#lesson-live-streak").textContent = lesson.streak;
    }

    async function finishLesson() {
        if (lesson.finished) return;
        lesson.finished = true;
        lessonHiddenInput.blur();

        const wpm = calcLessonWpm();
        const accuracy = calcLessonAccuracy();
        const passed = accuracy >= lesson.passAccuracy;

        playFinishSound();

        // Show results
        $("#lesson-result-wpm").textContent = wpm;
        $("#lesson-result-accuracy").textContent = accuracy;
        $("#lesson-result-errors").textContent = lesson.errors;
        $("#lesson-result-streak").textContent = lesson.bestStreak;

        const statusEl = $("#lesson-pass-status");
        if (passed) {
            statusEl.textContent = "Passed!";
            statusEl.className = "lesson-pass-status passed";
        } else {
            statusEl.textContent = `Need ${lesson.passAccuracy}% accuracy to pass. Try again!`;
            statusEl.className = "lesson-pass-status failed";
        }

        // Show/hide next button
        const nextBtn = $("#btn-lesson-next");
        if (passed && lesson.nextId) {
            nextBtn.style.display = "";
        } else {
            nextBtn.style.display = "none";
        }

        lessonResultsOverlay.classList.add("active");

        // Save result
        try {
            await fetch(`/api/lesson/${lesson.id}/result`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    wpm: wpm,
                    accuracy: accuracy,
                    errors: lesson.errors,
                    total_chars: lesson.totalTyped,
                    correct_chars: lesson.correctChars,
                }),
            });
        } catch (_) {}

        await flushCharErrors();
    }

    function exitLesson() {
        lesson.active = false;
        lesson.finished = false;
        lessonResultsOverlay.classList.remove("active");
        lessonActiveEl.style.display = "none";
        lessonBrowser.style.display = "block";
        loadLessons();
    }

    function retryLesson() {
        lessonResultsOverlay.classList.remove("active");
        startLesson(lesson.id);
    }

    function nextLesson() {
        lessonResultsOverlay.classList.remove("active");
        if (lesson.nextId) {
            startLesson(lesson.nextId);
        } else {
            exitLesson();
        }
    }

    // ===== WEAK KEYS PRACTICE =====

    const weakSection = $("#weak-keys-section");
    const weakPracticeActive = $("#weak-practice-active");
    const weakTextDisplay = $("#weak-text-display");
    const weakHiddenInput = $("#weak-hidden-input");
    const weakTypingContainer = $("#weak-typing-container");
    const weakClickHint = $("#weak-click-hint");
    const weakTimerBarFill = $("#weak-timer-bar-fill");
    const weakTimerText = $("#weak-timer-text");

    let weak = {
        active: false,
        text: "",
        chars: [],
        currentIndex: 0,
        errors: 0,
        correctChars: 0,
        totalTyped: 0,
        streak: 0,
        bestStreak: 0,
        started: false,
        finished: false,
        startTime: null,
        timerInterval: null,
        duration: 60,
        timeLeft: 60,
    };

    async function loadWeakKeysPreview() {
        try {
            const res = await fetch("/api/weak-keys");
            const data = await res.json();
            if (data.weak_keys.length === 0) {
                weakSection.style.display = "none";
                return;
            }
            weakSection.style.display = "block";
            const tagsEl = $("#weak-keys-tags");
            tagsEl.innerHTML = data.weak_keys.slice(0, 6).map((k) =>
                `<span class="weak-key-tag">${escapeHtml(k.char)}<span class="count">${k.count}x</span></span>`
            ).join("");
        } catch (_) {
            weakSection.style.display = "none";
        }
    }

    async function startWeakPractice() {
        try {
            const res = await fetch("/api/weak-keys/practice");
            const data = await res.json();
            if (!data.has_data) return;

            weak.active = true;
            weak.text = data.text;
            weak.chars = data.text.split("");
            weak.currentIndex = 0;
            weak.errors = 0;
            weak.correctChars = 0;
            weak.totalTyped = 0;
            weak.streak = 0;
            weak.bestStreak = 0;
            weak.started = false;
            weak.finished = false;
            weak.startTime = null;
            clearInterval(weak.timerInterval);
            weak.timeLeft = weak.duration;

            // Show weak key tags in header
            const keysEl = $("#weak-practice-keys");
            keysEl.innerHTML = data.weak_keys.map((k) =>
                `<span class="key-tag">${escapeHtml(k.char)}</span>`
            ).join("");

            renderWeakText();

            weakSection.style.display = "none";
            lessonBrowser.style.display = "none";
            weakPracticeActive.style.display = "block";
            weakHiddenInput.focus();
        } catch (_) {}
    }

    function renderWeakText() {
        renderTextToDisplay(weak.text, weakTextDisplay, weakHiddenInput, weakClickHint);
        updateWeakLiveStats();
        weakTimerBarFill.style.width = "100%";
        weakTimerBarFill.className = "timer-bar-fill";
        weakTimerText.className = "timer-text";
        weakTimerText.textContent = weak.timeLeft;
    }

    function handleWeakInput() {
        if (weak.finished) return;

        const inputVal = weakHiddenInput.value;
        if (inputVal.length === 0) return;

        const typedChar = inputVal[inputVal.length - 1];
        weakHiddenInput.value = "";

        if (!weak.started) {
            weak.started = true;
            weak.startTime = Date.now();
            weakClickHint.style.display = "none";
            startWeakTimer();
        }

        const expected = weak.chars[weak.currentIndex];
        const charSpan = weakTextDisplay.querySelector(`[data-index="${weak.currentIndex}"]`);
        const rect = charSpan ? charSpan.getBoundingClientRect() : null;

        weak.totalTyped++;

        if (typedChar === expected) {
            charSpan.classList.remove("current", "upcoming");
            charSpan.classList.add("correct");
            weak.correctChars++;
            weak.streak++;
            if (weak.streak > weak.bestStreak) weak.bestStreak = weak.streak;

            playKeySound();
            if (rect) spawnParticle(typedChar, rect.left + rect.width / 2, rect.top, true);

            if (weak.streak > 0 && weak.streak % 10 === 0) {
                playComboSound();
                if (rect) spawnComboFlash(weak.streak, rect.left, rect.top);
            }
        } else {
            charSpan.classList.remove("current", "upcoming");
            charSpan.classList.add("incorrect");
            weak.errors++;
            weak.streak = 0;
            recordCharError(expected, typedChar);

            playErrorSound();
            if (rect) spawnParticle(typedChar, rect.left + rect.width / 2, rect.top, false);
            weakTypingContainer.classList.add("error-flash");
            if (settings.screenShake) weakTypingContainer.classList.add("screen-shake");
            setTimeout(() => weakTypingContainer.classList.remove("error-flash", "screen-shake"), 150);
        }

        weak.currentIndex++;

        if (weak.currentIndex < weak.chars.length) {
            const next = weakTextDisplay.querySelector(`[data-index="${weak.currentIndex}"]`);
            if (next) {
                next.classList.remove("upcoming");
                next.classList.add("current");
                const lineHeight = parseFloat(getComputedStyle(weakTextDisplay).lineHeight);
                const firstCharTop = weakTextDisplay.querySelector('[data-index="0"]')?.offsetTop || 0;
                const currentTop = next.offsetTop;
                const linesScrolled = Math.floor((currentTop - firstCharTop) / lineHeight);
                if (linesScrolled > 0) {
                    weakTextDisplay.style.transform = `translateY(-${linesScrolled * lineHeight}px)`;
                }
            }
        } else {
            finishWeakPractice();
        }

        updateWeakLiveStats();
    }

    function startWeakTimer() {
        weak.timerInterval = setInterval(() => {
            weak.timeLeft--;
            weakTimerText.textContent = weak.timeLeft;

            const pct = (weak.timeLeft / weak.duration) * 100;
            weakTimerBarFill.style.width = pct + "%";

            if (pct <= 20) {
                weakTimerBarFill.className = "timer-bar-fill danger";
                weakTimerText.className = "timer-text danger";
            } else if (pct <= 40) {
                weakTimerBarFill.className = "timer-bar-fill warning";
                weakTimerText.className = "timer-text warning";
            }

            if (weak.timeLeft <= 0) finishWeakPractice();
        }, 1000);
    }

    function calcWeakWpm() {
        if (!weak.startTime) return 0;
        const elapsed = (Date.now() - weak.startTime) / 1000 / 60;
        if (elapsed === 0) return 0;
        return Math.round((weak.correctChars / 5) / elapsed);
    }

    function calcWeakAccuracy() {
        if (weak.totalTyped === 0) return 100;
        return Math.round((weak.correctChars / weak.totalTyped) * 100);
    }

    function updateWeakLiveStats() {
        $("#weak-live-wpm").textContent = calcWeakWpm();
        $("#weak-live-accuracy").textContent = calcWeakAccuracy();
        $("#weak-live-errors").textContent = weak.errors;
        $("#weak-live-streak").textContent = weak.streak;
    }

    async function finishWeakPractice() {
        if (weak.finished) return;
        weak.finished = true;
        clearInterval(weak.timerInterval);
        weakHiddenInput.blur();

        playFinishSound();
        await flushCharErrors();

        // Show results via the main results overlay
        const wpm = calcWeakWpm();
        const accuracy = calcWeakAccuracy();
        $("#result-wpm").textContent = wpm;
        $("#result-accuracy").textContent = accuracy;
        $("#result-errors").textContent = weak.errors;
        $("#result-streak").textContent = weak.bestStreak;
        $("#badge-wpm").style.display = "none";
        $("#badge-streak").style.display = "none";
        resultsOverlay.classList.add("active");
    }

    function exitWeakPractice() {
        weak.active = false;
        weak.finished = false;
        clearInterval(weak.timerInterval);
        resultsOverlay.classList.remove("active");
        weakPracticeActive.style.display = "none";
        weakSection.style.display = "block";
        lessonBrowser.style.display = "block";
        loadWeakKeysPreview();
    }

    // --- Events ---
    function bindEvents() {
        // Hidden input
        hiddenInput.addEventListener("input", handleInput);

        // Focus on container click
        typingContainer.addEventListener("click", () => hiddenInput.focus());

        // Focus on any keypress when test/lesson view active
        document.addEventListener("keydown", (e) => {
            // Lesson results overlay
            if (lesson.finished && lessonResultsOverlay.classList.contains("active")) {
                if (e.key === "Enter") { e.preventDefault(); retryLesson(); }
                if (e.key === "Escape") { exitLesson(); }
                return;
            }

            // Test/Weak results overlay
            if (resultsOverlay.classList.contains("active")) {
                if (e.key === "Enter") {
                    e.preventDefault();
                    if (weak.active) { resultsOverlay.classList.remove("active"); startWeakPractice(); }
                    else { restart(); }
                }
                if (e.key === "Escape") {
                    if (weak.active) { exitWeakPractice(); }
                    else { resultsOverlay.classList.remove("active"); }
                }
                return;
            }

            if (passageOverlay.classList.contains("active")) {
                if (e.key === "Escape") passageOverlay.classList.remove("active");
                return;
            }

            if (codeOverlay.classList.contains("active")) {
                if (e.key === "Escape") codeOverlay.classList.remove("active");
                return;
            }

            if (customOverlay.classList.contains("active")) {
                if (e.key === "Escape") customOverlay.classList.remove("active");
                return;
            }

            // Tab = restart (test mode only)
            if (e.key === "Tab" && $("#view-test").classList.contains("active")) {
                e.preventDefault();
                restart();
                return;
            }

            // Weak practice active: focus input
            if ($("#view-learn").classList.contains("active") && weak.active && !weak.finished) {
                if (e.target.closest(".lesson-active-header")) return;
                weakHiddenInput.focus();
                return;
            }

            // Lesson active: focus input
            if ($("#view-learn").classList.contains("active") && lesson.active && !lesson.finished) {
                if (e.target.closest(".lesson-active-header")) return;
                lessonHiddenInput.focus();
                return;
            }

            // Test active: focus input
            const testView = $("#view-test");
            if (testView.classList.contains("active") && !state.finished) {
                if (e.target.closest(".config-bar")) return;
                hiddenInput.focus();
            }
        });

        // Mode buttons
        $$("[data-mode]").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                $$("[data-mode]").forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                state.mode = btn.dataset.mode;
                if (state.mode === "passage") {
                    showPassageSelector();
                } else if (state.mode === "code") {
                    showCodeSelector();
                } else if (state.mode === "custom") {
                    showCustomTextOverlay();
                } else {
                    restart();
                }
            });
        });

        // Time buttons
        $$("[data-time]").forEach((btn) => {
            btn.addEventListener("click", () => {
                $$("[data-time]").forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                state.duration = parseInt(btn.dataset.time);
                state.timeLeft = state.duration;
                restart();
            });
        });

        // Restart button
        $("#btn-restart").addEventListener("click", restart);

        // Result overlay buttons
        $("#btn-retry").addEventListener("click", () => {
            if (weak.active) {
                resultsOverlay.classList.remove("active");
                startWeakPractice();
            } else {
                restart();
            }
        });
        $("#btn-close-results").addEventListener("click", () => {
            if (weak.active) {
                exitWeakPractice();
            } else {
                resultsOverlay.classList.remove("active");
            }
        });

        // Close overlays on outside click
        passageOverlay.addEventListener("click", (e) => {
            if (e.target === passageOverlay) passageOverlay.classList.remove("active");
        });
        codeOverlay.addEventListener("click", (e) => {
            if (e.target === codeOverlay) codeOverlay.classList.remove("active");
        });
        customOverlay.addEventListener("click", (e) => {
            if (e.target === customOverlay) customOverlay.classList.remove("active");
        });

        // Custom text events
        $("#btn-custom-start").addEventListener("click", startCustomText);
        $("#btn-custom-cancel").addEventListener("click", () => customOverlay.classList.remove("active"));

        // --- Weak keys events ---
        weakHiddenInput.addEventListener("input", handleWeakInput);
        weakTypingContainer.addEventListener("click", () => weakHiddenInput.focus());
        $("#btn-start-weak-practice").addEventListener("click", startWeakPractice);
        $("#btn-weak-back").addEventListener("click", exitWeakPractice);

        // --- Lesson events ---
        lessonHiddenInput.addEventListener("input", handleLessonInput);
        lessonTypingContainer.addEventListener("click", () => lessonHiddenInput.focus());
        $("#btn-lesson-back").addEventListener("click", exitLesson);
        $("#btn-lesson-retry").addEventListener("click", retryLesson);
        $("#btn-lesson-next").addEventListener("click", nextLesson);
        $("#btn-lesson-browse").addEventListener("click", exitLesson);

        // Stats mode filter
        $$("[data-stats-mode]").forEach((btn) => {
            btn.addEventListener("click", () => {
                $$("[data-stats-mode]").forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                statsMode = btn.dataset.statsMode === "all" ? null : btn.dataset.statsMode;
                loadStats();
            });
        });

        // Stats duration filter
        $$("[data-stats-duration]").forEach((btn) => {
            btn.addEventListener("click", () => {
                $$("[data-stats-duration]").forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                statsDuration = btn.dataset.statsDuration === "all" ? null : parseInt(btn.dataset.statsDuration);
                loadStats();
            });
        });

        // Nav tabs
        $$(".nav-tab").forEach((tab) => {
            tab.addEventListener("click", () => {
                $$(".nav-tab").forEach((t) => t.classList.remove("active"));
                tab.classList.add("active");
                $$(".view").forEach((v) => v.classList.remove("active"));
                $(`#view-${tab.dataset.view}`).classList.add("active");

                if (tab.dataset.view === "stats") loadStats();
                if (tab.dataset.view === "learn") { loadWeakKeysPreview(); loadLessons(); }
            });
        });
    }

    // --- Boot ---
    init();
})();
