const API_BASE = '/api/v1/admin';

// DOM Elements
const els = {
    // Metrics
    activeBookings: document.getElementById('val-active-bookings'),
    avgResponse: document.getElementById('val-avg-response'),
    successRate: document.getElementById('val-success-rate'),
    
    // Before State
    rawRequest: document.getElementById('val-raw-request'),
    language: document.getElementById('val-language'),
    parsedSlots: document.getElementById('val-parsed-slots'),
    
    // After State
    providerName: document.getElementById('val-provider-name'),
    providerRating: document.getElementById('val-provider-rating'),
    providerDistance: document.getElementById('val-provider-distance'),
    finalPrice: document.getElementById('val-final-price'),
    bookingStatus: document.getElementById('val-booking-status'),
    providerSkills: document.getElementById('val-provider-skills'),
    providerRatingUpdate: document.getElementById('val-provider-rating-update'),
    
    // Timeline
    timeline: document.getElementById('timeline-container')
};

/**
 * Fetch and update Live System Metrics
 */
async function fetchMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const m = data.metrics;
            els.activeBookings.innerText = m.active_bookings;
            els.avgResponse.innerText = `${m.avg_response_time_ms} ms`;
            els.successRate.innerText = `${m.success_rate_percent}%`;
        }
    } catch (error) {
        console.error("Failed to fetch metrics:", error);
    }
}

/**
 * Fetch and update the Demo State (Before, After, Trace)
 */
async function fetchDemoState() {
    // Show loading state on button click
    els.timeline.innerHTML = '<div class="timeline-empty">Simulating AI Workflow...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/demo-state`);
        const data = await response.json();
        
        if (data.status === 'success') {
            updateBeforeState(data.before_state);
            updateAfterState(data.after_state);
            updateTimeline(data.agent_trace);
        }
    } catch (error) {
        console.error("Failed to fetch demo state:", error);
        els.timeline.innerHTML = '<div class="timeline-empty" style="color: #ef4444;">Simulation failed. Backend unavailable.</div>';
    }
}

/**
 * Update Before Panel UI
 */
function updateBeforeState(before) {
    els.rawRequest.innerText = `"${before.raw_request}"`;
    els.language.innerText = before.detected_language;
    
    // Render slots
    els.parsedSlots.innerHTML = '';
    for (const [key, val] of Object.entries(before.parsed_slots)) {
        els.parsedSlots.innerHTML += `
            <div class="slot-tag">
                <span class="slot-key">${key}:</span>
                <span class="slot-val">${val}</span>
            </div>
        `;
    }
}

/**
 * Update After Panel UI
 */
function updateAfterState(after) {
    els.providerName.innerText = after.selected_provider.name;
    els.providerRating.innerText = after.selected_provider.rating;
    els.providerDistance.innerText = after.selected_provider.distance;
    els.finalPrice.innerText = after.final_price;
    els.bookingStatus.innerText = after.booking_status;
    els.providerRatingUpdate.innerText = after.provider_rating_update;
    
    // Render skills
    els.providerSkills.innerHTML = '';
    after.selected_provider.skills.forEach(skill => {
        els.providerSkills.innerHTML += `
            <div class="skill-tag">
                <span class="material-symbols-outlined" style="font-size: 14px; color: var(--success);">check_circle</span>
                ${skill}
            </div>
        `;
    });
}

/**
 * Update Timeline UI with animations
 */
function updateTimeline(trace) {
    els.timeline.innerHTML = '';
    
    trace.forEach((step, index) => {
        // Stagger animation delay
        const delay = index * 0.15;
        
        const stepHTML = `
            <div class="timeline-step" style="animation-delay: ${delay}s;">
                <div class="step-marker">${step.step}</div>
                <div class="step-agent">${step.agent}</div>
                <div class="step-action">${step.action}</div>
            </div>
        `;
        els.timeline.innerHTML += stepHTML;
    });
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    fetchMetrics();
    fetchDemoState();
    
    // Poll metrics every 3 seconds
    setInterval(fetchMetrics, 3000);
});
