const quoteForm = document.querySelector("#quote-form");
const formNote = document.querySelector("#form-note");
const serviceTypeInput = document.querySelector("#service-type");
const trailerSizeInput = document.querySelector("#trailer-size");
const debrisTypeInput = document.querySelector("#debris-type");
const accessTypeInput = document.querySelector("#access-type");
const weightEstimateInput = document.querySelector("#weight-estimate");
const textEstimateButton = document.querySelector("#text-estimate");
const bookDepositButton = document.querySelector("#book-deposit");
const payBalanceButton = document.querySelector("#pay-balance");
const estimateTotal = document.querySelector("#estimate-total");
const estimateIncluded = document.querySelector("#estimate-included");
const estimateOverage = document.querySelector("#estimate-overage");
const estimateWindow = document.querySelector("#estimate-window");
const estimateNote = document.querySelector("#estimate-note");
const paymentDeposit = document.querySelector("#payment-deposit");
const paymentFlowNote = document.querySelector("#payment-flow-note");
const bookingGrid = document.querySelector("#booking-grid");

const serviceProfiles = {
  self: {
    label: "Self-load rental",
    note: "Premium multi-day rental because the trailer stays on-site for several days.",
    paymentNote:
      "Self-load rentals use a larger deposit because the trailer stays on-site until pickup.",
  },
  loading: {
    label: "Quick load & haul",
    note: "Faster-turn option when you want the trailer in and out instead of left for days.",
    paymentNote:
      "Quick load and haul can use a smaller deposit because the trailer turns faster and is not left on-site for several days.",
  },
};

const sizeProfiles = {
  ten: {
    label: "10 yard trailer",
    selfBasePrice: 849,
    loadingBasePrice: 649,
    includedTons: 2,
    baseOveragePerTon: 120,
    selfDeposit: 250,
    loadingDeposit: 99,
    includedDays: 3,
    extraDayFee: 45,
  },
  fifteen: {
    label: "15 yard trailer",
    selfBasePrice: 949,
    loadingBasePrice: 749,
    includedTons: 2,
    baseOveragePerTon: 120,
    selfDeposit: 300,
    loadingDeposit: 149,
    includedDays: 3,
    extraDayFee: 55,
  },
};

const accessProfiles = {
  easy: {
    label: "Easy access / driveway / garage",
    loadingAdjustment: 0,
  },
  moderate: {
    label: "Moderate carry / backyard / some distance",
    loadingAdjustment: 85,
  },
  hard: {
    label: "Stairs / difficult access / heavy hand loading",
    loadingAdjustment: 165,
  },
};

const debrisProfiles = {
  household: {
    label: "Mixed household junk",
    priceAdjustment: 0,
    tonAdjustment: 0,
    note: "Good fit for furniture, bagged trash, boxes, garage junk, and normal cleanout loads.",
  },
  remodel: {
    label: "Light remodel debris",
    priceAdjustment: 35,
    tonAdjustment: 0,
    note: "Good for drywall, cabinets, trim, flooring, and lighter remodel debris.",
  },
  yard: {
    label: "Yard waste / brush",
    priceAdjustment: 0,
    tonAdjustment: 0,
    note: "Best for brush, branches, fencing, and general yard cleanup material.",
  },
  roofing: {
    label: "Roofing / shingles",
    priceAdjustment: 65,
    tonAdjustment: -0.5,
    note: "Shingles are dense, so the included weight is lower and disposal gets more expensive.",
  },
  dense: {
    label: "Concrete / dirt / tile",
    priceAdjustment: 95,
    tonAdjustment: -0.5,
    note: "Very dense materials hit weight limits quickly. Text photos before booking.",
  },
};

const bookingStatuses = {
  open: {
    label: "Open",
    className: "status-open",
  },
  held: {
    label: "Hold",
    className: "status-held",
  },
  booked: {
    label: "Booked",
    className: "status-booked",
  },
};

// Update these statuses as deposits come in or jobs are completed.
const availabilityTemplate = [
  { offset: 0, ten: "open", fifteen: "held" },
  { offset: 1, ten: "booked", fifteen: "open" },
  { offset: 2, ten: "open", fifteen: "open" },
  { offset: 3, ten: "held", fifteen: "booked" },
  { offset: 4, ten: "open", fifteen: "open" },
  { offset: 5, ten: "booked", fifteen: "open" },
  { offset: 6, ten: "open", fifteen: "held" },
];

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatBookingDate(date) {
  return {
    weekday: new Intl.DateTimeFormat("en-US", { weekday: "short" }).format(date),
    monthDay: new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(date),
  };
}

function renderBookingCalendar() {
  if (!bookingGrid) {
    return;
  }

  const today = new Date();

  bookingGrid.innerHTML = availabilityTemplate
    .map((slot) => {
      const date = new Date(today);
      date.setDate(today.getDate() + slot.offset);

      const formattedDate = formatBookingDate(date);
      const tenStatus = bookingStatuses[slot.ten] || bookingStatuses.open;
      const fifteenStatus = bookingStatuses[slot.fifteen] || bookingStatuses.open;

      return `
        <article class="booking-day">
          <p class="booking-weekday">${formattedDate.weekday}</p>
          <p class="booking-date">${formattedDate.monthDay}</p>
          <div class="booking-row">
            <span>10 YD</span>
            <span class="status-pill ${tenStatus.className}">${tenStatus.label}</span>
          </div>
          <div class="booking-row">
            <span>15 YD</span>
            <span class="status-pill ${fifteenStatus.className}">${fifteenStatus.label}</span>
          </div>
        </article>
      `;
    })
    .join("");
}

function buildEstimate() {
  const selectedService = serviceProfiles[serviceTypeInput?.value] || serviceProfiles.self;
  const selectedSize = sizeProfiles[trailerSizeInput?.value] || sizeProfiles.ten;
  const selectedProfile = debrisProfiles[debrisTypeInput?.value] || debrisProfiles.household;
  const selectedAccess = accessProfiles[accessTypeInput?.value] || accessProfiles.easy;
  const estimatedWeight = Number.parseFloat(weightEstimateInput?.value || "2");
  const includedTons = Math.max(1, selectedSize.includedTons + selectedProfile.tonAdjustment);
  const overagePerTon = selectedSize.baseOveragePerTon;
  const extraWeight = Math.max(0, estimatedWeight - includedTons);
  const loadingAdjustment =
    serviceTypeInput?.value === "loading" ? selectedAccess.loadingAdjustment : 0;
  const basePrice =
    serviceTypeInput?.value === "loading"
      ? selectedSize.loadingBasePrice
      : selectedSize.selfBasePrice;
  const selectedDeposit =
    serviceTypeInput?.value === "loading"
      ? selectedSize.loadingDeposit
      : selectedSize.selfDeposit;
  const windowText =
    serviceTypeInput?.value === "loading"
      ? "Fast-turn visit"
      : `Includes up to ${selectedSize.includedDays} days`;
  const total =
    basePrice +
    selectedProfile.priceAdjustment +
    loadingAdjustment +
    extraWeight * overagePerTon;

  if (estimateTotal) {
    estimateTotal.textContent = formatCurrency(total);
  }

  if (estimateIncluded) {
    estimateIncluded.textContent = `Includes up to ${includedTons.toFixed(1)} tons`;
  }

  if (estimateOverage) {
    estimateOverage.textContent = `${formatCurrency(overagePerTon)} per extra ton`;
  }

  if (estimateWindow) {
    estimateWindow.textContent = windowText;
  }

  if (estimateNote) {
    const serviceNote =
      serviceTypeInput?.value === "loading"
        ? `${selectedService.note} Access setting: ${selectedAccess.label}.`
        : `${selectedService.note} Extra rental days are ${formatCurrency(selectedSize.extraDayFee)} per day after the included window.`;

    estimateNote.textContent = `${selectedSize.label} selected. ${selectedProfile.note} ${serviceNote} Final total depends on actual landfill scale weight, rental days, and prohibited items.`;
  }

  if (paymentDeposit) {
    paymentDeposit.textContent = formatCurrency(selectedDeposit);
  }

  if (paymentFlowNote) {
    const extraChargeLine =
      serviceTypeInput?.value === "loading"
        ? "Access adjustments are confirmed before the job starts."
        : `Extra rental days are ${formatCurrency(selectedSize.extraDayFee)} per day after the included window.`;

    paymentFlowNote.textContent = `${selectedService.paymentNote} ${extraChargeLine} Remaining balance and any overweight charges are confirmed after service and dump scale weight.`;
  }

  if (bookDepositButton) {
    bookDepositButton.textContent = `Book with ${formatCurrency(selectedDeposit)} Deposit`;
  }

  return {
    selectedService,
    selectedSize,
    selectedProfile,
    selectedAccess,
    estimatedWeight,
    includedTons,
    overagePerTon,
    selectedDeposit,
    total,
    windowText,
  };
}

function buildQuoteMessage() {
  const formData = new FormData(quoteForm);
  const {
    selectedService,
    selectedSize,
    selectedProfile,
    selectedAccess,
    estimatedWeight,
    includedTons,
    overagePerTon,
    selectedDeposit,
    total,
    windowText,
  } = buildEstimate();
  const name = formData.get("name")?.toString().trim() || "New customer";
  const phone = formData.get("phone")?.toString().trim() || "Not provided";
  const address = formData.get("address")?.toString().trim() || "Not provided";
  const timing = formData.get("timing")?.toString().trim() || "Flexible";
  const details = formData.get("details")?.toString().trim() || "No project details provided.";

  return {
    subject: `Trailer Estimate Request - ${selectedSize.label} - ${name}`,
    selectedDeposit,
    bodyLines: [
      `Service type: ${selectedService.label}`,
      `Trailer size: ${selectedSize.label}`,
      `Debris type: ${selectedProfile.label}`,
      `Job access: ${selectedAccess.label}`,
      `Schedule preference: ${timing}`,
      `Service window: ${windowText}`,
      `Estimated weight: ${estimatedWeight.toFixed(1)} tons`,
      `Estimated total: ${formatCurrency(total)}`,
      `Suggested deposit: ${formatCurrency(selectedDeposit)}`,
      `Included tonnage: ${includedTons.toFixed(1)} tons`,
      `Overage rate: ${formatCurrency(overagePerTon)} per extra ton`,
      `Extra day fee: ${formatCurrency(selectedSize.extraDayFee)} per day after included window`,
      `Name: ${name}`,
      `Phone: ${phone}`,
      `Address: ${address}`,
      "",
      "Project details:",
      details,
    ],
  };
}

function openDispatchText(lines, statusMessage) {
  const smsBody = encodeURIComponent(lines.join("\n"));
  window.location.href = `sms:+19563159677?body=${smsBody}`;

  if (formNote) {
    formNote.textContent = statusMessage;
  }
}

if (serviceTypeInput && trailerSizeInput && debrisTypeInput && accessTypeInput && weightEstimateInput) {
  serviceTypeInput.addEventListener("change", buildEstimate);
  trailerSizeInput.addEventListener("change", buildEstimate);
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
    window.location.href = `mailto:dispatch@bulldogcontainers.com?subject=${subject}&body=${body}`;

    if (formNote) {
      formNote.textContent =
        "Your email draft is ready. You can also text dispatch photos if you want a tighter quote before sending a deposit.";
    }
  });
}

if (textEstimateButton) {
  textEstimateButton.addEventListener("click", () => {
    if (!quoteForm) {
      return;
    }

    const message = buildQuoteMessage();
    openDispatchText(
      [
        "Hi Bulldog Containers, I need a trailer quote.",
        ...message.bodyLines,
      ],
      "Your text draft is opening. If SMS does not launch on this device, call or copy the estimate details into a text manually."
    );
  });
}

if (bookDepositButton) {
  bookDepositButton.addEventListener("click", () => {
    if (!quoteForm) {
      return;
    }

    const message = buildQuoteMessage();
    openDispatchText(
      [
        `Hi Bulldog Containers, I want to book with the ${formatCurrency(message.selectedDeposit)} deposit.`,
        ...message.bodyLines,
        "",
        "Please send the deposit payment details and confirm the next available slot.",
      ],
      "Your deposit text draft is opening. Dispatch can reply with payment details and confirm the booking slot."
    );
  });
}

if (payBalanceButton) {
  payBalanceButton.addEventListener("click", () => {
    if (!quoteForm) {
      return;
    }

    const message = buildQuoteMessage();
    openDispatchText(
      [
        "Hi Bulldog Containers, I need to pay my remaining balance.",
        ...message.bodyLines,
        "",
        "Please send the final amount and payment details.",
      ],
      "Your remaining-balance text draft is opening. Dispatch can reply with the final amount and payment details."
    );
  });
}

renderBookingCalendar();
