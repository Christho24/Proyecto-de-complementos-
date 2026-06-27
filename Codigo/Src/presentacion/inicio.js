document.querySelectorAll(".tarjeta").forEach(tarjeta => {
  tarjeta.addEventListener("pointermove", evento => {
    const limites = tarjeta.getBoundingClientRect();
    tarjeta.style.setProperty("--x", `${evento.clientX - limites.left}px`);
    tarjeta.style.setProperty("--y", `${evento.clientY - limites.top}px`);
  });
});
