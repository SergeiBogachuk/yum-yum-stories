const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");
const revealItems = document.querySelectorAll("[data-reveal]");
const quoteForm = document.querySelector("#quote-form");
const formNote = document.querySelector("#form-note");

if (menuToggle && siteNav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = siteNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
  });

  siteNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      siteNav.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
    });
  });
}

if ("IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    },
    {
      threshold: 0.15,
    }
  );

  revealItems.forEach((item, index) => {
    item.style.transitionDelay = `${Math.min(index * 60, 360)}ms`;
    revealObserver.observe(item);
  });
} else {
  revealItems.forEach((item) => item.classList.add("is-visible"));
}

if (quoteForm) {
  quoteForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(quoteForm);
    const projectType = formData.get("project_type")?.toString().trim() || "Garage or household cleanout";
    const name = formData.get("name")?.toString().trim() || "New customer";
    const phone = formData.get("phone")?.toString().trim() || "Not provided";
    const address = formData.get("address")?.toString().trim() || "Not provided";
    const timing = formData.get("timing")?.toString().trim() || "Flexible";
    const details = formData.get("details")?.toString().trim() || "No project details provided.";

    const subject = encodeURIComponent(`Dumpster Trailer Quote Request - ${name}`);
    const body = encodeURIComponent(
      [
        `Project type: ${projectType}`,
        `Name: ${name}`,
        `Phone: ${phone}`,
        `Address: ${address}`,
        "Requested package: Single trailer rental",
        `Preferred timing: ${timing}`,
        "",
        "Project details:",
        details,
      ].join("\n")
    );

    window.location.href = `mailto:hello@irondropdumpsters.com?subject=${subject}&body=${body}`;

    if (formNote) {
      formNote.textContent = "Your email draft is ready. Replace the demo phone and email with your real contact info before launch.";
    }
  });
}
