let zoomLevel = 0.4;

const wrapper = document.getElementById("chart-wrapper");
const container = document.getElementById("chart-container");
const zoomValueBtn = document.getElementById("zoom-value");

container.style.transform = `translate(-50%, 0) scale(${zoomLevel})`;
zoomValueBtn.innerText = Math.round(zoomLevel * 100) + "%";

function applyZoom() {
    container.style.transform = `translate(-50%, 0) scale(${zoomLevel})`;
    zoomValueBtn.innerText = Math.round(zoomLevel * 100) + "%";
}

function zoomIn() {
    zoomLevel += 0.1;
    applyZoom();
}

function zoomOut() {
    if (zoomLevel > 0.2) zoomLevel -= 0.1;
    applyZoom();
}

function resetZoom() {
    zoomLevel = 1;
    applyZoom();
}

let isDragging = false, startX, startY;

function startDrag(x, y) {
    isDragging = true;
    startX = x - container.offsetLeft;
    startY = y - container.offsetTop;
    wrapper.style.cursor = "grabbing";
}

function moveDrag(x, y) {
    if (!isDragging) return;
    container.style.left = (x - startX) + "px";
    container.style.top = (y - startY) + "px";
}

function endDrag() {
    isDragging = false;
    wrapper.style.cursor = "grab";
}

wrapper.addEventListener("mousedown", e => startDrag(e.clientX, e.clientY));
wrapper.addEventListener("mousemove", e => moveDrag(e.clientX, e.clientY));
wrapper.addEventListener("mouseup", endDrag);
wrapper.addEventListener("mouseleave", endDrag);

wrapper.addEventListener("touchstart", e => startDrag(e.touches[0].clientX, e.touches[0].clientY));
wrapper.addEventListener("touchmove", e => {
    moveDrag(e.touches[0].clientX, e.touches[0].clientY);
    e.preventDefault();
});
wrapper.addEventListener("touchend", endDrag);
