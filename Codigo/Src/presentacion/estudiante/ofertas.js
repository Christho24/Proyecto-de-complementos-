const empresaId = document.body.dataset.empresaId;
const estudianteId = document.body.dataset.estudianteId;
const empresaNombre = document.body.dataset.empresaNombre;
const empresaIniciales = document.body.dataset.empresaIniciales;
const lista = document.querySelector("#lista-ofertas");
const estadoCarga = document.querySelector("#estado-carga");
const contador = document.querySelector("#contador");
const buscador = document.querySelector("#buscar");
const orden = document.querySelector("#orden");
const modal = document.querySelector("#modal-postulacion");
const formulario = document.querySelector("#formulario-postulacion");
const carta = formulario.querySelector("textarea");
const campoArchivoCv = document.querySelector("#campo-archivo-cv");
const inputCurriculum = formulario.elements.curriculum;
const vistaPerfilCvv = document.querySelector("#vista-perfil-cvv");
const notificacion = document.querySelector("#notificacion");
let ofertas = [];

const escapar = (texto = "") =>
  String(texto).replace(/[&<>"']/g, caracter => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  })[caracter]);

const moneda = valor =>
  new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(valor);

function notificar(mensaje, error = false) {
  notificacion.textContent = mensaje;
  notificacion.className = `notificacion visible${error ? " error" : ""}`;
  window.setTimeout(() => notificacion.classList.remove("visible"), 3600);
}

function ofertasVisibles() {
  const termino = buscador.value.trim().toLocaleLowerCase("es");
  const datos = ofertas.filter(oferta =>
    `${oferta.titulo} ${oferta.carrera} ${oferta.modalidad} ${oferta.ubicacion}`
      .toLocaleLowerCase("es").includes(termino)
  );
  if (orden.value === "sueldo") datos.sort((a, b) => b.sueldo_max - a.sueldo_max);
  if (orden.value === "titulo") datos.sort((a, b) => a.titulo.localeCompare(b.titulo, "es"));
  if (orden.value === "recientes") datos.sort((a, b) => new Date(b.fecha_publicacion) - new Date(a.fecha_publicacion));
  return datos;
}

function renderizar() {
  const datos = ofertasVisibles();
  estadoCarga.hidden = true;
  contador.textContent = `${datos.length} ${datos.length === 1 ? "oferta habilitada" : "ofertas habilitadas"}`;
  if (!datos.length) {
    lista.innerHTML = `<div class="estado"><div><h3>No encontramos ofertas</h3><p>No hay oportunidades habilitadas o no coinciden con tu búsqueda.</p></div></div>`;
    return;
  }
  lista.innerHTML = datos.map(oferta => `
    <article class="oferta${oferta.postulada ? " postulada" : ""}">
      <div class="tope"><span class="empresa-icono">${escapar(empresaIniciales)}</span><span class="modalidad">${escapar(oferta.modalidad)}</span></div>
      <h3>${escapar(oferta.titulo)}</h3>
      <p class="empresa-nombre">${escapar(empresaNombre)}</p>
      <p class="descripcion">${escapar(oferta.descripcion)}</p>
      <div class="datos">
        <span>◎ ${escapar(oferta.ubicacion)}</span>
        <span>▷ ${escapar(oferta.jornada)}</span>
        <span>▣ ${escapar(oferta.carrera)}</span>
      </div>
      <div class="pie">
        <span class="sueldo">${moneda(oferta.sueldo_min)} - ${moneda(oferta.sueldo_max)}</span>
        ${oferta.postulada
          ? `<button class="boton secundario postular" type="button" disabled>Ya postulaste</button>`
          : `<button class="boton primario postular" type="button" data-id="${oferta.id}" data-titulo="${escapar(oferta.titulo)}">Postular</button>`}
      </div>
    </article>
  `).join("");
}

async function cargarOfertas() {
  estadoCarga.hidden = false;
  lista.innerHTML = "";
  try {
    const ruta = `/api/empresas/${encodeURIComponent(empresaId)}/ofertas/estudiante?estudiante_id=${encodeURIComponent(estudianteId)}`;
    const respuesta = await fetch(ruta);
    const resultado = await respuesta.json();
    if (!respuesta.ok) throw new Error(resultado.error || "No fue posible cargar las ofertas.");
    ofertas = resultado.datos;
    renderizar();
  } catch (error) {
    estadoCarga.hidden = true;
    contador.textContent = "No disponible";
    lista.innerHTML = `<div class="estado"><div><h3>No pudimos cargar las ofertas</h3><p>${escapar(error.message)}</p></div></div>`;
  }
}

lista.addEventListener("click", evento => {
  const boton = evento.target.closest(".postular");
  if (!boton || boton.disabled) return;
  formulario.elements.oferta_id.value = boton.dataset.id;
  document.querySelector("#titulo-modal").textContent = boton.dataset.titulo;
  modal.showModal();
});

[buscador, orden].forEach(control => control.addEventListener("input", renderizar));
document.querySelector(".cerrar").addEventListener("click", () => modal.close());
document.querySelector(".cancelar").addEventListener("click", () => modal.close());
modal.addEventListener("click", evento => { if (evento.target === modal) modal.close(); });
carta.addEventListener("input", () => {
  document.querySelector("#caracteres").textContent = `${carta.value.length} / 1500`;
});

function actualizarOrigenCv() {
  const origen = formulario.elements.origen_cv.value;
  const usaArchivo = origen === "archivo";
  campoArchivoCv.hidden = !usaArchivo;
  vistaPerfilCvv.hidden = usaArchivo;
  inputCurriculum.required = usaArchivo;
  if (!usaArchivo) inputCurriculum.value = "";
}

formulario.elements.origen_cv.forEach(control =>
  control.addEventListener("change", actualizarOrigenCv)
);

formulario.addEventListener("submit", async evento => {
  evento.preventDefault();
  const ofertaId = formulario.elements.oferta_id.value;
  const boton = formulario.querySelector("[type=submit]");
  boton.disabled = true;
  boton.textContent = "Enviando...";
  try {
    const datos = new FormData(formulario);
    datos.set("estudiante_id", estudianteId);
    const respuesta = await fetch(`/api/ofertas/${encodeURIComponent(ofertaId)}/postulaciones`, {
      method: "POST",
      body: datos
    });
    const resultado = await respuesta.json();
    if (!respuesta.ok) throw new Error(resultado.error || "No fue posible postular.");
    ofertas = ofertas.map(oferta =>
      oferta.id === ofertaId ? { ...oferta, postulada: true } : oferta
    );
    formulario.reset();
    actualizarOrigenCv();
    document.querySelector("#caracteres").textContent = "0 / 1500";
    modal.close();
    renderizar();
    notificar(resultado.mensaje);
  } catch (error) {
    notificar(error.message, true);
  } finally {
    boton.disabled = false;
    boton.textContent = "Enviar postulación";
  }
});

actualizarOrigenCv();
cargarOfertas();
