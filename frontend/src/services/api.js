// ===============================
// 🌐 Configuração base da API
// ===============================
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// -------------------------------
// 🔐 Helper: obter token JWT do localStorage
// -------------------------------
const getAuthToken = () => localStorage.getItem('token');

// -------------------------------
// ⚙️ Helper: requisições autenticadas com tratamento de erros
// -------------------------------
const fetchWithAuth = async (url, options = {}) => {
  const token = getAuthToken();

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Erro desconhecido' }));
    throw new Error(error.error || error.msg || `Erro ${response.status}`);
  }

  if (response.status === 204) return {}; // Sem conteúdo
  return response.json();
};

// ===============================
// 👤 Autenticação (Login, Registro, Logout)
// ===============================
export const authService = {
  getCurrentUser: () => fetchWithAuth('/user/me'),
  login: async (username, password) =>
    fetchWithAuth('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  register: async (username, email, password, name) =>
    fetchWithAuth('/users', {
      method: 'POST',
      body: JSON.stringify({ username, email, password, name }),
    }),

  logout: async () => {
    try {
      await fetchWithAuth('/logout', { method: 'POST' });
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },
};

// ===============================
// 🛒 Produtos
// ===============================
export const productService = {
  // Público
  getAll: () => fetchWithAuth('/products'),

  // Admin
  create: (productData) =>
    fetchWithAuth('/admin/products', {
      method: 'POST',
      body: JSON.stringify(productData),
    }),

  update: (id, productData) =>
    fetchWithAuth(`/admin/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(productData),
    }),

  delete: (id) =>
    fetchWithAuth(`/admin/products/${id}`, {
      method: 'DELETE',
    }),
};

// ===============================
// ❤️ Favoritos
// ===============================
export const favoriteService = {
  getAll: async () => fetchWithAuth("/favorites", "GET"),

  add: async (productId) =>
    fetchWithAuth('/favorites', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId }),
    }),

  remove: async (productId) =>
    fetchWithAuth(`/favorites/${productId}`, {
      method: 'DELETE',
    }),
};

// ===============================
// ⭐ Reviews
// ===============================
export const reviewService = {
  getAll: () => fetchWithAuth('/reviews'),

  create: (productId, rating, comment) =>
    fetchWithAuth('/reviews', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, rating, comment }),
    }),
};

// ===============================
// 💡 Dicas
// ===============================
export const tipService = {
  getAll: () => fetchWithAuth('/tips'),

  create: (title, content, category) =>
    fetchWithAuth('/admin/tips', {
      method: 'POST',
      body: JSON.stringify({ title, content, category }),
    }),

  update: (id, data) =>
    fetchWithAuth(`/admin/tips/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id) =>
    fetchWithAuth(`/admin/tips/${id}`, {
      method: 'DELETE',
    }),
};

// ===============================
// ❓ FAQs
// ===============================
export const faqService = {
  getAll: () => fetchWithAuth('/faqs'),

  create: (question, answer) =>
    fetchWithAuth('/admin/faqs', {
      method: 'POST',
      body: JSON.stringify({ question, answer }),
    }),

  update: (id, data) =>
    fetchWithAuth(`/admin/faqs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id) =>
    fetchWithAuth(`/admin/faqs/${id}`, {
      method: 'DELETE',
    }),
};

// ===============================
// 👥 Usuários
// ===============================
export const userService = {
  getAll: () => fetchWithAuth('/admin/users'),

  createAdmin: (username, email, password, name) =>
    fetchWithAuth('/admin/users', {
      method: 'POST',
      body: JSON.stringify({ username, email, password, name }),
    }),

  update: (userId, userData) =>
    fetchWithAuth(`/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    }),

  delete: (userId) =>
    fetchWithAuth(`/admin/users/${userId}`, {
      method: 'DELETE',
    }),

  updateSelf: (userData) =>
    fetchWithAuth('/user/update', {
      method: 'PUT',
      body: JSON.stringify(userData),
    }),

  changePassword: (passwordData) =>
    fetchWithAuth('/user/change-password', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    }),

  deleteAccount: () =>
    fetchWithAuth('/user/delete-account', {
      method: 'DELETE',
    }),
};

// ===============================
// 🌐 Redes Sociais
// ===============================
export const socialMediaService = {
  getAll: () => fetchWithAuth('/social-media'),

  create: (platform, url) =>
    fetchWithAuth('/admin/social-media', {
      method: 'POST',
      body: JSON.stringify({ platform, url }),
    }),

  update: (id, data) =>
    fetchWithAuth(`/admin/social-media/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id) =>
    fetchWithAuth(`/admin/social-media/${id}`, {
      method: 'DELETE',
    }),
};

// ===============================
// 📈 Dashboard (Admin)
// ===============================
export const dashboardService = {
  getStats: () => fetchWithAuth('/admin/stats'),
  getUserGrowth: async () => {
    const data = await fetchWithAuth('/admin/user-growth')
    return data.growth || []
  },
  getProductRatings: async () => {
    try {
      const data = await fetchWithAuth('/admin/product-ratings');
      return data.ratings || [];
    } catch (error) {
      console.warn("Endpoint /admin/product-ratings não encontrado. O gráfico ficará vazio.");
      return [];
    }
  },
};

// ===============================
// 🤖 ChatBot
// ===============================
export const chatService = {
  sendMessage: (message) =>
    fetchWithAuth('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    }),
};

export default {
  authService,
  productService,
  favoriteService,
  reviewService,
  tipService,
  faqService,
  userService,
  socialMediaService,
  dashboardService,
  chatService
};
