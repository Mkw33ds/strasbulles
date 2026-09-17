document.addEventListener("DOMContentLoaded", () => {
  const button = document.querySelector("[data-menu-button]");
  const menu = document.querySelector("[data-mobile-menu]");
  if (button && menu) {
    button.addEventListener("click", () => {
      const open = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!open));
      menu.hidden = open;
    });
  }
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && button && menu) {
      button.setAttribute("aria-expanded", "false");
      menu.hidden = true;
      button.focus();
    }
  });
});

