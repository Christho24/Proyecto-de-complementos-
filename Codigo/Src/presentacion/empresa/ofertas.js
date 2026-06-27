const empresaId = document.body.dataset.empresaId;
const lista = document.querySelector("#lista-ofertas");
const estadoCarga = document.querySelector("#estado-carga");
const total = document.querySelector("#total-ofertas");
const buscador = document.querySelector("#buscar");
const modal = document.querySelector("#modal-oferta");
const formulario = document.querySelector("#formulario-oferta");
const notificacion = document.querySelector("#notificacion");
const modalPostulantes = document.querySelector("#modal-postulantes");
const listaPostulantes = document.querySelector("#lista-postulantes");
let ofertas = [];

const escapar = (texto = "") =>
  String(texto).replace(/[&<>"']/g, caracter => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  })[caracter]);

const moneda = valor =>
  new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(valor);

const fecha = valor =>
  valor ? new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(valor)) : "Fecha no disponible";

function textoLista(valores = []) {
  return Array.isArray(valores) && valores.length ? valores.join(", ") : "Sin datos";
}

function renderizarCv(postulacion) {
  if (postulacion.origen_cv !== "plataforma") {
    return `
      <a class="boton descargar-cv" href="/api/curriculums/${encodeURIComponent(postulacion.cv_archivo_id)}">
        Descargar CV
      </a>
    `;
  }
  const perfil = postulacion.perfil_cvv || {};
  const datos = perfil.datos_personales || {};
  return `
    <section class="cvv-postulacion">
      <h4>PerfilCVV de la plataforma</h4>
      <p>${escapar(datos.correo || "")} ${perfil.carrera ? `· ${escapar(perfil.carrera)}` : ""}</p>
      <dl>
        <div><dt>Especialidades</dt><dd>${escapar(textoLista(perfil.especialidades))}</dd></div>
        <div><dt>Roles</dt><dd>${escapar(textoLista(perfil.roles))}</dd></div>
        <div><dt>Intereses</dt><dd>${escapar(textoLista(perfil.intereses))}</dd></div>
        <div><dt>Experiencia</dt><dd>${escapar(textoLista(perfil.experiencia))}</dd></div>
        <div><dt>Logros</dt><dd>${escapar(textoLista(perfil.logros))}</dd></div>
      </dl>
    </section>
  `;
}

function mostrarNotificacion(mensaje, esError = false) {
  notificacion.textContent = mensaje;
  notificacion.className = `notificacion visible${esError ? " error" : ""}`;
  window.setTimeout(() => notificacion.classList.remove("visible"), 3500);
}

function renderizar(datos) {
  total.textContent = ofertas.length;
  document.querySelector("#total-postulantes").textContent =
    ofertas.reduce((suma, oferta) => suma + (oferta.total_postulantes || 0), 0);
  estadoCarga.hidden = true;
  if (!datos.length) {
    lista.innerHTML = `<div class="estado"><div><h3>No hay ofertas para mostrar</h3><p>Publica una nueva oportunidad para comenzar.</p></div></div>`;
    return;
  }
  lista.innerHTML = datos.map(oferta => `
    <article class="oferta">
      <span class="inicial">${escapar(oferta.titulo.charAt(0).toUpperCase())}</span>
      <div>
        <h3>${escapar(oferta.titulo)}</h3>
        <div class="metadatos">
          <span>◉ ${escapar(oferta.ubicacion)}</span>
          <span>◷ ${escapar(oferta.jornada)}</span>
          <span>⌁ ${escapar(oferta.modalidad)}</span>
          <span>${escapar(oferta.carrera)}</span>
          <span>${moneda(oferta.sueldo_min)} – ${moneda(oferta.sueldo_max)}</span>
        </div>
      </div>
      <div class="acciones-oferta">
        <span class="etiqueta">Habilitada</span>
        <div class="fecha">Publicada ${fecha(oferta.fecha_publicacion)}</div>
        <button class="boton postulantes-btn" type="button"
          data-id="${oferta.id}" data-titulo="${escapar(oferta.titulo)}">
          Ver postulantes (${oferta.total_postulantes || 0})
        </button>
        <button class="boton eliminar-oferta-btn" type="button"
          data-id="${oferta.id}" data-titulo="${escapar(oferta.titulo)}">
          Eliminar
        </button>
      </div>
    </article>
  `).join("");
}

async function cargarOfertas() {
  estadoCarga.hidden = false;
  lista.innerHTML = "";
  try {
    const respuesta = await fetch(`/api/empresas/${encodeURIComponent(empresaId)}/ofertas`);
    const resultado = await respuesta.json();
    if (!respuesta.ok) throw new Error(resultado.error || "No fue posible cargar las ofertas.");
    ofertas = resultado.datos;
    renderizar(ofertas);
  } catch (error) {
    estadoCarga.hidden = true;
    lista.innerHTML = `<div class="estado"><div><h3>No pudimos cargar las ofertas</h3><p>${escapar(error.message)}</p></div></div>`;
  }
}

buscador.addEventListener("input", () => {
  const termino = buscador.value.trim().toLocaleLowerCase("es");
  renderizar(ofertas.filter(oferta =>
    `${oferta.titulo} ${oferta.carrera} ${oferta.modalidad}`.toLocaleLowerCase("es").includes(termino)
  ));
});

document.querySelector("#abrir-formulario").addEventListener("click", () => modal.showModal());
document.querySelector("#modal-oferta .cerrar").addEventListener("click", () => modal.close());
document.querySelector(".cancelar").addEventListener("click", () => modal.close());
modal.addEventListener("click", evento => {
  if (evento.target === modal) modal.close();
});

lista.addEventListener("click", async evento => {
  const eliminar = evento.target.closest(".eliminar-oferta-btn");
  if (eliminar) {
    const titulo = eliminar.dataset.titulo;
    if (!window.confirm(`¿Eliminar la oferta "${titulo}"?`)) return;
    eliminar.disabled = true;
    eliminar.textContent = "Eliminando...";
    try {
      const respuesta = await fetch(
        `/api/empresas/${encodeURIComponent(empresaId)}/ofertas/${encodeURIComponent(eliminar.dataset.id)}`,
        { method: "DELETE" }
      );
      const resultado = await respuesta.json();
      if (!respuesta.ok) throw new Error(resultado.error || "No fue posible eliminar la oferta.");
      ofertas = ofertas.filter(oferta => oferta.id !== eliminar.dataset.id);
      renderizar(ofertas);
      mostrarNotificacion(resultado.mensaje);
    } catch (error) {
      eliminar.disabled = false;
      eliminar.textContent = "Eliminar";
      mostrarNotificacion(error.message, true);
    }
    return;
  }

  const boton = evento.target.closest(".postulantes-btn");
  if (!boton) return;
  document.querySelector("#titulo-postulantes").textContent = boton.dataset.titulo;
  listaPostulantes.innerHTML = `<div class="estado"><span class="spinner"></span><p>Cargando postulantes…</p></div>`;
  modalPostulantes.showModal();
  try {
    const ruta = `/api/ofertas/${encodeURIComponent(boton.dataset.id)}/postulaciones?empresa_id=${encodeURIComponent(empresaId)}`;
    const respuesta = await fetch(ruta);
    const resultado = await respuesta.json();
    if (!respuesta.ok) throw new Error(resultado.error || "No fue posible cargar las postulaciones.");
    if (!resultado.datos.length) {
      listaPostulantes.innerHTML = `<div class="estado"><div><h3>Aún no hay postulantes</h3><p>Las postulaciones aparecerán aquí.</p></div></div>`;
      return;
    }
    listaPostulantes.innerHTML = resultado.datos.map(postulacion => `
      <article class="postulante">
        <span class="avatar-postulante">${escapar(postulacion.estudiante_nombre.split(" ").map(p => p[0]).slice(0, 2).join(""))}</span>
        <div class="datos-postulante">
          <h3>${escapar(postulacion.estudiante_nombre)}</h3>
          <p>Postuló el ${fecha(postulacion.fecha)} · Estado: ${escapar(postulacion.estado)}</p>
          ${postulacion.carta_presentacion
            ? `<blockquote>${escapar(postulacion.carta_presentacion)}</blockquote>`
            : `<p class="sin-carta">Sin carta de presentación.</p>`}
        </div>
        ${renderizarCv(postulacion)}
      </article>
    `).join("");
  } catch (error) {
    listaPostulantes.innerHTML = `<div class="estado"><div><h3>No se pudo cargar</h3><p>${escapar(error.message)}</p></div></div>`;
  }
});

document.querySelectorAll(".cerrar-postulantes").forEach(boton =>
  boton.addEventListener("click", () => modalPostulantes.close())
);

formulario.addEventListener("submit", async evento => {
  evento.preventDefault();
  const boton = formulario.querySelector("[type=submit]");
  boton.disabled = true;
  boton.textContent = "Publicando…";
  const datos = Object.fromEntries(new FormData(formulario));
  datos.sueldo_min = Number(datos.sueldo_min);
  datos.sueldo_max = Number(datos.sueldo_max);
  try {
    const respuesta = await fetch(`/api/empresas/${encodeURIComponent(empresaId)}/ofertas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos)
    });
    const resultado = await respuesta.json();
    if (!respuesta.ok) throw new Error(resultado.error || "No fue posible publicar.");
    formulario.reset();
    modal.close();
    mostrarNotificacion(resultado.mensaje);
    await cargarOfertas();
  } catch (error) {
    mostrarNotificacion(error.message, true);
  } finally {
    boton.disabled = false;
    boton.textContent = "Publicar oferta";
  }
});

cargarOfertas();
