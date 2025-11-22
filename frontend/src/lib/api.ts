const API_BASE = "http://localhost:5000";

export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  location_lat: number;
  location_long: number;
  roles: string[];
}

export interface Food {
  id: number;
  donor_id: number;
  food_name: string;
  quantity: number;
  expiry_date: string;
  status: string;
}

export interface Request {
  id: number;
  receiver_id: number;
  food_type: string;
  quantity: number;
  urgency_level: string;
  deadline: string;
  status: string;
}

export interface Transaction {
  id: number;
  donor_id: number;
  receiver_id: number;
  food_id: number;
  status: string;
  created_at: string;
}

const getHeaders = () => ({
  "Content-Type": "application/json",
  "X-User-Id": localStorage.getItem("user_id") || "",
});

async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Request failed" }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }
  return response.json();
}

// User APIs
export const api = {
  auth: {
    register: async (data: {
      name: string;
      email: string;
      password: string;
      phone: string;
      location_lat: number;
      location_long: number;
      roles: string[];
    }) => {
      const response = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },

    login: async (email: string, password: string) => {
      const response = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      return handleResponse(response);
    },
  },

  user: {
    getProfile: async (userId: number) => {
      const response = await fetch(`${API_BASE}/profile/${userId}`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    updateProfile: async (userId: number, data: Partial<User>) => {
      const response = await fetch(`${API_BASE}/profile/${userId}`, {
        method: "PUT",
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },
  },

  food: {
    add: async (data: {
      food_name: string;
      quantity: number;
      expiry_date: string;
    }) => {
      const response = await fetch(`${API_BASE}/food/add`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },

    getMyFoods: async (donorId: number) => {
      const response = await fetch(`${API_BASE}/food/my/${donorId}`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    update: async (foodId: number, data: Partial<Food>) => {
      const response = await fetch(`${API_BASE}/food/update/${foodId}`, {
        method: "PUT",
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },

    delete: async (foodId: number) => {
      const response = await fetch(`${API_BASE}/food/delete/${foodId}`, {
        method: "DELETE",
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    getNearbyRequests: async () => {
      const response = await fetch(`${API_BASE}/food/requests/nearby`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    match: async (foodId: number, requestId: number) => {
      const response = await fetch(`${API_BASE}/food/match/${foodId}/${requestId}`, {
        method: "POST",
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    getDonorTransactions: async (donorId: number) => {
      const response = await fetch(`${API_BASE}/food/transactions/donor/${donorId}`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },
  },

  requests: {
    create: async (data: {
      receiver_id: number;
      food_type: string;
      quantity: number;
      urgency_level: string;
      deadline: string;
    }) => {
      const response = await fetch(`${API_BASE}/requests/add_request`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },

    getAll: async () => {
      const response = await fetch(`${API_BASE}/requests/all`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    update: async (requestId: number, data: Partial<Request>) => {
      const response = await fetch(`${API_BASE}/requests/update/${requestId}`, {
        method: "PUT",
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },

    cancel: async (requestId: number) => {
      const response = await fetch(`${API_BASE}/requests/cancel/${requestId}`, {
        method: "DELETE",
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    accept: async (foodId: number, receiverId: number) => {
      const response = await fetch(`${API_BASE}/requests/accept/${foodId}`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ receiver_id: receiverId }),
      });
      return handleResponse(response);
    },
  },

  transactions: {
    create: async (data: {
      donor_id: number;
      receiver_id: number;
      food_id: number;
    }) => {
      const response = await fetch(`${API_BASE}/transactions/create`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },

    getAll: async () => {
      const response = await fetch(`${API_BASE}/transactions/all`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    getUserTransactions: async (userId: number) => {
      const response = await fetch(`${API_BASE}/transactions/user/${userId}`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },

    updateStatus: async (txnId: number, status: string) => {
      const response = await fetch(`${API_BASE}/transactions/update/${txnId}`, {
        method: "PUT",
        headers: getHeaders(),
        body: JSON.stringify({ status }),
      });
      return handleResponse(response);
    },
  },
};

console.log("API BASE FROM api.ts =", API_BASE);