export const API_URL = 'http://localhost:8000/api/v1';

export const fetchApi = async (endpoint, options = {}) => {
  const token = localStorage.getItem("cineguide_token");
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem("cineguide_token");
    localStorage.removeItem("cineguide_user");
    window.dispatchEvent(new Event('auth-unauthorized'));
  }

  const data = await response.json().catch(() => null);
  
  if (!response.ok) {
    throw new Error(data?.detail || data?.message || 'Something went wrong');
  }

  return data;
};
