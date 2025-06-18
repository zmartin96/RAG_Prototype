document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const questionInput = document.querySelector("#question");
    const output = document.querySelector("#output");
    const loading = document.querySelector("#loading");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const question = questionInput.value.trim();
        if (!question) return;

        output.innerHTML = "";
        loading.style.display = "block";

        const res = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        const data = await res.json();
        loading.style.display = "none";

        output.innerHTML = `
      <h2>Answer</h2>
      <p>${data.answer}</p>
      <h3>Citations</h3>
      <ul>${data.citations.map(c => `<li>Job ${c.jobno} | EQNO ${c.eqno} | Shift ${c.shift} | Date ${c.prod_date}</li>`).join("")}</ul>
    `;
    });
});
