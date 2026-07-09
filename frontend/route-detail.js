const routeTabs = Array.from(document.querySelectorAll('[data-route-tab]'));
const routePanels = Array.from(document.querySelectorAll('[data-route-panel]'));

function setRouteTab(targetTab) {
  routeTabs.forEach((tab) => {
    const isActive = tab.dataset.routeTab === targetTab;
    tab.classList.toggle('route-tabs__button--active', isActive);
    tab.setAttribute('aria-selected', String(isActive));
  });

  routePanels.forEach((panel) => {
    panel.hidden = panel.dataset.routePanel !== targetTab;
  });
}

routeTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    setRouteTab(tab.dataset.routeTab);
  });
});
