<template>
  <div>
    <div v-if="jwtValido" class="visitas-container">
      
      <h2 style="text-align: center; margin-bottom: 2rem; color: #34495e; font-size: 2rem; font-family: 'Poppins', sans-serif; font-weight: 600;">🐾 Consultas</h2>

      <div class="consultas-panel">
        
        <div class="panel-header">
          <h3>Mis Consultas</h3>
          <div v-if="info_usuario && info_usuario.tipo === 'prop_mascota'">
            <button class="add-btn" @click="abrirModalCrear">
              ➕ Añadir consulta
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Cargando consultas...</p>
        </div>

        <div v-else-if="consultas.length > 0" class="items-list">
          <div v-for="consulta in consultas" :key="consulta.id" class="item-card" @click="abrirModalDetalle(consulta)">
            <div class="item-content">
              <div class="item-header-row">
                <h3 class="item-title">{{ consulta.titulo }}</h3>
                <span :class="['estado-badge', consulta.estado]">{{ formatEstado(consulta.estado) }}</span>
              </div>
              <p class="item-desc">{{ consulta.descripcion }}</p>
              <div v-if="info_usuario && consulta.estado === 'PENDIENTE' && info_usuario.tipo === 'veterinario'">
                <button class="add-btn" @click.stop="abrirModalResponder(consulta)">
                  <i class="fas fa-reply"></i> Responder
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="no-items">
          <p>No tienes consultas registradas en este momento.</p>
        </div>

      </div> </div>

    <div v-else class="no-auth">
      <p>Inicia sesión para ver tus consultas.</p>
    </div>

    <div v-if="modalVisible" class="modal-overlay" @click="cerrarModalCrear">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">Nueva consulta</h2>
        <form @submit.prevent="crearConsulta">
          <div class="form-group">
            <label>Título</label>
            <input type="text" v-model="formCrear.titulo" required maxlength="50" />
          </div>
          <div class="form-group">
            <label>Descripción</label>
            <textarea v-model="formCrear.descripcion" required maxlength="500"></textarea>
          </div>
          <div class="form-group">
            <label>Mascota</label>
            <select v-model="formCrear.mascota_id" required>
              <option value="" disabled>Selecciona mascota...</option>
              <option v-for="m in mascotas" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Veterinario (Opcional)</label>
            <select v-model="formCrear.vet_id">
              <option :value="null">Consulta genérica a la clínica</option>
              <option v-for="v in veterinarios" :key="v.id" :value="v.id">{{ v.nombre }}</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-save">Guardar</button>
            <button type="button" class="btn-cancel" @click="cerrarModalCrear">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="modalDetalleVisible" class="modal-overlay" @click="cerrarModalDetalle">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header-detalle">
          <h2>Detalle de la Consulta</h2>
          <button class="close-x" @click="cerrarModalDetalle">&times;</button>
        </div>
        <div class="detalle-body">
          <div class="bubble consulta-bubble">
            <span class="bubble-label">Consulta original</span>
            <h3>{{ consultaSeleccionada?.titulo }}</h3>
            <p>{{ consultaSeleccionada?.descripcion }}</p>
          </div>
          <div v-for="res in respuestasDetalle" :key="res.id" class="bubble respuesta-bubble">
            <span class="bubble-label"><i class="fas fa-user-md"></i> Respuesta de veterinario</span>
            <h3>{{ res.titulo }}</h3><p>{{ res.descripcion }}</p>
          </div>
        </div>
        <div v-if="info_usuario && info_usuario.tipo === 'prop_mascota' && consultaSeleccionada?.estado === 'PENDIENTE' && respuestasDetalle.length > 0" class="modal-actions" style="justify-content: center;">
          <button class="btn-save" @click="finalizarConsulta(consultaSeleccionada.id)">Finalizar Consulta</button>
        </div>
      </div>
    </div>

    <div v-if="modalResponderVisible" class="modal-overlay" @click="cerrarModalResponder">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">Responder</h2>
        <form @submit.prevent="enviarRespuesta">
          <div class="form-group"><label>Título</label><input type="text" v-model="formResponder.titulo" required /></div>
          <div class="form-group"><label>Descripción</label><textarea v-model="formResponder.descripcion" required></textarea></div>
          <div class="modal-actions">
            <button type="submit" class="btn-save">Enviar</button>
            <button type="button" class="btn-cancel" @click="cerrarModalResponder">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import api from '../api/axios';

export default {
  name: 'ConsultasView',
  data() {
    return {
      info_usuario: null,
      jwtValido: false,
      loading: false,
      consultas: [],
      modalVisible: false,
      mascotas: [],
      veterinarios: [],
      formCrear: {
        titulo: '',
        descripcion: '',
        mascota_id: '',
        vet_id: null
      },
      modalDetalleVisible: false,
      consultaSeleccionada: null,
      respuestasDetalle: [],
      cargandoRespuestas: false,
      modalResponderVisible: false,
      formResponder: {
        titulo: '',
        descripcion: ''
      }
    };
  },
  async created() {
    this.checkAuth();
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem('jwt');
      const user = localStorage.getItem('user');
      if (token && user) {
        this.info_usuario = JSON.parse(user);
        this.jwtValido = true;
        this.obtenerConsultas();
      }
    },
    async obtenerConsultas() {
      this.loading = true;
      try {
        const res = await api.get(`http://localhost:5000/api/consultas/getConsultas/${this.info_usuario.id}`);
        this.consultas = res.data;
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
    formatEstado(e) {
      return e === 'RESUELTA' ? 'RESUELTA' : 'PENDIENTE';
    },
    async abrirModalDetalle(c) {
      this.consultaSeleccionada = c;
      this.modalDetalleVisible = true;
      const res = await api.get(`http://localhost:5000/api/consultas/getRespuestas/${c.id}`);
      this.respuestasDetalle = res.data;
    },
    async finalizarConsulta(id) {
      await api.put(`http://localhost:5000/api/consultas/cerrar-consulta/${id}`);
      this.modalDetalleVisible = false;
      this.obtenerConsultas();
    },
    async abrirModalCrear() {
      this.modalVisible = true;
      const resM = await api.get('http://localhost:5000/api/mascotas/listar-tus-mascotas');
      this.mascotas = resM.data;
      const resV = await api.get('http://localhost:5000/api/consultas/get-veterinarios');
      this.veterinarios = resV.data;
    },
    cerrarModalCrear() {
      this.modalVisible = false;
    },
    async crearConsulta() {
      await api.post('http://localhost:5000/api/consultas/crear-consulta', this.formCrear);
      this.cerrarModalCrear();
      this.obtenerConsultas();
    },
    abrirModalResponder(c) {
      this.consultaSeleccionada = c;
      this.modalResponderVisible = true;
    },
    cerrarModalResponder() {
      this.modalResponderVisible = false;
    },
    async enviarRespuesta() {
      await api.post(`http://localhost:5000/api/consultas/responder-consulta/${this.consultaSeleccionada.id}`, this.formResponder);
      this.cerrarModalResponder();
      this.obtenerConsultas();
    },
    cerrarModalDetalle() {
      this.modalDetalleVisible = false;
    }
  }
};
</script>
<style scoped src="./css/Consultas.css"></style>