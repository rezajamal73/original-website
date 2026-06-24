let zoomLevel = 0.8;

let isDragging = false;
let startX = 0;
let startY = 0;
let currentX = 0;
let currentY = 0;

const wrapper = document.getElementById("chart-wrapper");
const container = document.getElementById("chart-container");
const zoomValueBtn = document.getElementById("zoom-value");

/* ================= APPLY ================= */
function applyTransform() {
    container.style.transform =
        `translateX(-50%) translate(${currentX}px, ${currentY}px) scale(${zoomLevel})`;
    zoomValueBtn.innerText = Math.round(zoomLevel * 100) + "%";
}

applyTransform();

/* ================= ZOOM ================= */
function zoomIn() {
    zoomLevel += 0.1;
    applyTransform();
}

function zoomOut() {
    if (zoomLevel > 0.2) {
        zoomLevel -= 0.1;
        applyTransform();
    }
}

function resetZoom() {
    zoomLevel = 1;
    currentX = 0;
    currentY = 0;
    applyTransform();
}

/* ================= DRAG ================= */
function startDrag(x, y) {
    isDragging = true;
    startX = x - currentX;
    startY = y - currentY;
    wrapper.style.cursor = "grabbing";
}

function moveDrag(x, y) {
    if (!isDragging) return;
    currentX = x - startX;
    currentY = y - startY;
    applyTransform();
}

function endDrag() {
    isDragging = false;
    wrapper.style.cursor = "grab";
}

/* ================= EVENTS ================= */
wrapper.addEventListener("mousedown", e => startDrag(e.clientX, e.clientY));
wrapper.addEventListener("mousemove", e => moveDrag(e.clientX, e.clientY));
wrapper.addEventListener("mouseup", endDrag);
wrapper.addEventListener("mouseleave", endDrag);

wrapper.addEventListener("touchstart", e =>
    startDrag(e.touches[0].clientX, e.touches[0].clientY)
);
wrapper.addEventListener("touchmove", e => {
    moveDrag(e.touches[0].clientX, e.touches[0].clientY);
    e.preventDefault();
});
wrapper.addEventListener("touchend", endDrag);
