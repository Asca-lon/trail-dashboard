const sidebar = document.querySelector("[data-sidebar]");
const sidebarToggleButton = document.querySelector("[data-sidebar-toggle]");
const sidebarCloseButton = document.querySelector("[data-sidebar-close]");

function setSidebarState(isOpen) {
  if (!sidebar || !sidebarToggleButton) {
    return;
  }

  sidebar.hidden = !isOpen;
  sidebar.classList.toggle("sidebar--open", isOpen);
  sidebarToggleButton.setAttribute("aria-expanded", String(isOpen));
  sidebarToggleButton.setAttribute("aria-label", isOpen ? "사이드바 닫기" : "사이드바 열기");
}

function openSidebar() {
  setSidebarState(true);
}

function closeSidebar() {
  setSidebarState(false);
}

function toggleSidebar() {
  const isOpen = sidebarToggleButton?.getAttribute("aria-expanded") === "true";

  setSidebarState(!isOpen);
}

if (sidebarToggleButton) {
  sidebarToggleButton.addEventListener("click", toggleSidebar);
}

if (sidebarCloseButton) {
  sidebarCloseButton.addEventListener("click", closeSidebar);
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeSidebar();
  }
});

setSidebarState(false);
