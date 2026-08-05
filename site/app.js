const API_URL = "https://4qcaviqsrb.execute-api.sa-east-1.amazonaws.com";

async function carregarTickets() {
  const resposta = await fetch(`${API_URL}/tickets`);
  const dados = await resposta.json();

  document.getElementById("resumo").textContent =
    `${dados.total} ticket(s) na fila`;

  const lista = document.getElementById("lista-tickets");
  lista.innerHTML = "";

  dados.tickets.forEach(ticket => {
    const div = document.createElement("div");
    div.className = `ticket urgencia-${ticket.urgencia} ${ticket.status === "revisado" ? "revisado" : ""}`;

    div.innerHTML = `
      <strong>${ticket.categoria} — ${ticket.urgencia}</strong>
      <p>${ticket.texto_bruto}</p>
      <small>Status: ${ticket.status}</small><br>
      ${ticket.status !== "revisado"
        ? `<button onclick="marcarRevisado('${ticket.id}')">Marcar como revisado</button>`
        : ""}
    `;

    lista.appendChild(div);
  });
}

async function marcarRevisado(id) {
  await fetch(`${API_URL}/tickets/${id}`, { method: "PATCH" });
  carregarTickets();
}

carregarTickets();