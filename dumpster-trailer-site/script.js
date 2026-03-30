const quoteForm = document.querySelector("#quote-form");
const formNote = document.querySelector("#form-note");
const serviceTypeInput = document.querySelector("#service-type");
const debrisTypeInput = document.querySelector("#debris-type");
const accessTypeInput = document.querySelector("#access-type");
const weightEstimateInput = document.querySelector("#weight-estimate");
const textEstimateButton = document.querySelector("#text-estimate");
const estimateTotal = document.querySelector("#estimate-total");
const estimateIncluded = document.querySelector("#estimate-included");
const estimateOverage = document.querySelector("#estimate-overage");
const estimateNote = document.querySelector("#estimate-note");

const serviceProfiles = {
  self: {
    label: "Trailer drop-off only",
    laborFee: 0,
    note: "Lower price because the customer loads the trailer.",
  },
  loading: {
    label: "We load it for you",
    laborFee: 195,
    note: "Higher price because the job includes loading labor, handling time, and hauling coordination.",
  },
};

const accessProfiles = {
  easy: {
    label: "Easy access / driveway / garage",
    loadingAdjustment: 0,
  },
  moderate: {
    label: "Moderate carry / backyard / some distance",
    loadingAdjustment: 75,
  },
  hard: {
    label: "Stairs / difficult access / heavy hand loading",
    loadingAdjustment: 150,
  },
};

const debrisProfiles = {
  household: {
    label: "Mixed household junk",
    basePrice: 429,
    includedTons: 2,
    overagePerTon: 85,
    note: "Good fit for garage junk, furniture, boxes, bagged trash, and normal cleanout loads.",
  },
  remodel: {
    label: "Light remodel debris",
    basePrice: 439,
    includedTons: 2,
    overagePerTon: 95,
    note: "Good for drywall, cabinets, trim, flooring, and mixed renovation debris.",
  },
  yard: {
    label: "Yard waste / brush",
    basePrice: 419,
    includedTons: 2,
    overagePerTon: 75,
    note: "Best for branches, brush, fence panels, and general yard cleanup material.",
  },
  roofing: {
    label: "Roofing / shingles",
    basePrice: 469,
    includedTons: 1.5,
    overagePerTon: 110,
    note: "Shingles are dense, so the included weight is lower and overage is higher.",
  },
  dense: {
    label: "Concrete / dirt / tile",
    basePrice: 489,
    includedTons: 1,
    overagePerTon: 120,
    note: "Very dense materials hit weight limits quickly. Text photos if you are not sure.",
  },
};

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function buildEstimate() {
  const selectedService = serviceProfiles[serviceTypeInput?.value] || serviceProfiles.self;
  const selectedProfile = debrisProfiles[debrisTypeInput?.value] || debrisProfiles.household;
  const selectedAccess = accessProfiles[accessTypeInput?.value] || accessProfiles.easy;
  const estimatedWeight = Number.parseFloat(weightEstimateInput?.value || "2");
  const extraWeight = Math.max(0, estimatedWeight - selectedProfile.includedTons);
  const loadingAdjustment =
    serviceTypeInput?.value === "loading" ? selectedAccess.loadingAdjustment : 0;
  const total =
    selectedProfile.basePrice +
    selectedService.laborFee +
    loadingAdjustment +
    extraWeight * selectedProfile.overagePerTon;

  if (estimateTotal) {
    estimateTotal.textContent = formatCurrency(total);
  }

  if (estimateIncluded) {
    estimateIncluded.textContent = `Includes up to ${selectedProfile.includedTons.toFixed(1)} tons`;
  }

  if (estimateOverage) {
    estimateOverage.textContent = `${formatCurrency(selectedProfile.overagePerTon)} per extra ton`;
  }

  if (estimateNote) {
    const accessNote =
      serviceTypeInput?.value === "loading"
        ? ` ${selectedService.note} Access setting: ${selectedAccess.label}.`
        : ` ${selectedService.note}`;
    estimateNote.textContent = `${selectedProfile.note}${accessNote} Final total depends on actual landfill scale weight, access, and prohibited items.`;
  }

  return {
    selectedService,
    selectedProfile,
    selectedAccess,
    estimatedWeight,
    total,
  };
}

function buildQuoteMessage() {
  const formData = new FormData(quoteForm);
  const { selectedService, selectedProfile, selectedAccess, estimatedWeight, total } = buildEstimate();
  const name = formData.get("name")?.toString().trim() || "New customer";
  const phone = formData.get("phone")?.toString().trim() || "Not provided";
  const address = formData.get("address")?.toString().trim() || "Not provided";
  const timing = formData.get("timing")?.toString().trim() || "Flexible";
  const details = formData.get("details")?.toString().trim() || "No project details provided.";

  return {
    subject: `Dumpster Trailer Estimate Request - ${name}`,
    bodyLines: [
      `Service type: ${selectedService.label}`,
      `Debris type: ${selectedProfile.label}`,
      `Job access: ${selectedAccess.label}`,
      `Estimated weight: ${estimatedWeight.toFixed(1)} tons`,
      `Estimated total: ${formatCurrency(total)}`,
      `Included tonnage: ${selectedProfile.includedTons.toFixed(1)} tons`,
      `Overage rate: ${formatCurrency(selectedProfile.overagePerTon)} per extra ton`,
      `Name: ${name}`,
      `Phone: ${phone}`,
      `Address: ${address}`,
      `Preferred timing: ${timing}`,
      "",
      "Project details:",
      details,
    ],
  };
}

if (serviceTypeInput && debrisTypeInput && accessTypeInput && weightEstimateInput) {
  serviceTypeInput.addEventListener("change", buildEstimate);
  debrisTypeInput.addEventListener("change", buildEstimate);
  accessTypeInput.addEventListener("change", buildEstimate);
  weightEstimateInput.addEventListener("change", buildEstimate);
  buildEstimate();
}

if (quoteForm) {
  quoteForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const message = buildQuoteMessage();
    const subject = encodeURIComponent(message.subject);
    const body = encodeURIComponent(message.bodyLines.join("\n"));
    window.location.href = `mailto:hello@irondropdumpsters.com?subject=${subject}&body=${body}`;

    if (formNote) {
      formNote.textContent = "Your email draft is ready. You can also text dispatch photos if you want a tighter quote.";
    }
  });
}

if (textEstimateButton) {
  textEstimateButton.addEventListener("click", () => {
    if (!quoteForm) {
      return;
    }

    const message = buildQuoteMessage();
    const smsBody = encodeURIComponent(
      [
        "Hi IronDrop, I need a trailer quote.",
        ...message.bodyLines,
      ].join("\n")
    );

    window.location.href = `sms:+19563159677?body=${smsBody}`;

    if (formNote) {
      formNote.textContent = "Your text draft is opening. If SMS does not launch on this device, call or copy the estimate details into a text manually.";
    }
  });
}
