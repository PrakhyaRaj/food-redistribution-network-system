const API_BASE = "http://127.0.0.1:5000";

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

export interface Activity {
  _id: string;
  activity_type: string;
  user_id?: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface AnalyticsSummary {
  total_food_saved_kg: number;
  total_people_fed: number;
  total_carbon_saved: number;
  weekly_trend: number;
}

export interface FoodImage {
  _id: string;
  food_id: number;  // Changed to number to match your Food interface
  image_data: string;
  mime_type: string;
  caption?: string;
  created_at: string;
}

export interface FoodNote {
  _id: string;
  food_id: number;
  note_type: string;
  content: string;
  metadata: {
    priority: 'high' | 'medium' | 'low';
    tags?: string[];
  };
  created_at: string;
}

// Auth storage keys
const TOKEN_KEY = "token";
const USER_ID_KEY = "user_id";

export function setAuthToken(token: string | null) {
  if (token) {
    // Ensure we're storing the raw token without "Bearer " prefix
    const cleanToken = token.startsWith("Bearer ") ? token.slice(7) : token;
    localStorage.setItem(TOKEN_KEY, cleanToken);
    console.log("✅ Token stored in localStorage");
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function getAuthToken(): string | null {
  const token = localStorage.getItem(TOKEN_KEY);
  console.log("🔍 Retrieved token from localStorage:", token ? "Present" : "Missing");
  return token;
}

export function setUserId(id: string | number | null) {
  if (id !== null && id !== undefined) {
    localStorage.setItem(USER_ID_KEY, String(id));
    console.log("✅ User ID stored:", id);
  } else {
    localStorage.removeItem(USER_ID_KEY);
  }
}

export function getUserId(): string | null {
  return localStorage.getItem(USER_ID_KEY);
}

const getHeaders = (withJson = true): Record<string, string> => {
  const headers: Record<string, string> = {};
  if (withJson) headers["Content-Type"] = "application/json";
  
  const token = getAuthToken();
  if (token) {
    // Add Bearer prefix when sending
    headers["Authorization"] = `Bearer ${token}`;
    console.log("🔍 Sending Authorization header with token");
  } else {
    console.log("❌ No token available for Authorization header");
  }
  
  const userId = getUserId();
  headers["X-User-Id"] = userId || "";
  console.log("🔍 Headers being sent:", headers);
  
  return headers;
};

// Update your handleResponse function in api.ts to log more details
async function handleResponse(response: Response) {
  const status = response.status;
  const url = response.url;
  
  console.log("🔍 API Response - URL:", url, "Status:", status);
  
  // Log request headers for debugging
  console.log("🔍 Request was made to:", url);
  
  if (!response.ok) {
    const text = await response.text();
    console.log("🔍 API Error - Raw response:", text);
    
    try {
      const parsed = text ? JSON.parse(text) : null;
      const message = parsed?.message || parsed?.error || parsed?.msg || text || `HTTP ${status}`;
      console.log("❌ API Error Message:", message);
      throw new Error(message);
    } catch (e) {
      throw new Error(text || `HTTP ${status}`);
    }
  }

  try {
    const data = await response.json();
    console.log("✅ API Success - Data received");
    return data;
  } catch (err) {
    return null;
  }
}

// Add this test function to your api.ts file
export const testToken = async () => {
  try {
    console.log("🧪 Testing token...");
    
    // Check what's in localStorage
    const token = localStorage.getItem("token");
    const userId = localStorage.getItem("user_id");
    console.log("🧪 localStorage token:", token);
    console.log("🧪 localStorage user_id:", userId);
    
    const response = await fetch(`${API_BASE}/auth/debug-token`, {
      method: "GET",
      headers: getHeaders(),
    });
    
    console.log("🧪 Test response status:", response.status);
    const result = await response.json();
    console.log("🧪 Token test result:", result);
    return result;
  } catch (error) {
    console.error("🧪 Token test failed:", error);
    return null;
  }
};

// --- API surface: auth stores token from header or body so subsequent calls include Authorization ---
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
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: getHeaders(true),
        body: JSON.stringify(data),
        // If your backend switched to cookie sessions, uncomment:
        // credentials: 'include',
      });

      // capture token from Authorization header if present
      const headerToken = res.headers.get("Authorization");
      if (headerToken) setAuthToken(headerToken);

      const body = await handleResponse(res);
      // fallback: token in JSON body
      if (body && (body.token || body.access_token)) {
        setAuthToken(body.token || body.access_token);
      }
      // store user id if returned
      if (body && body.user && body.user.id) setUserId(body.user.id);
      else if (body && body.id) setUserId(body.id);

      return body;
    },

    login: async (email: string, password: string) => {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: getHeaders(true),
        body: JSON.stringify({ email, password }),
      });

      const body = await handleResponse(res);
      console.log("🔍 Login response body:", body);

      // Store token and user data
      if (body && body.access_token) {
        setAuthToken(body.access_token);
        console.log("✅ Token stored after login");
      }
  
      if (body && body.user_id) {
        setUserId(body.user_id);
        console.log("✅ User ID stored after login:", body.user_id);
      } else if (body && body.user && body.user.id) {
        setUserId(body.user.id);
        console.log("✅ User ID stored after login:", body.user.id);
      }

      return body;
    },

    logout: async () => {
      setAuthToken(null);
      setUserId(null);
      try {
        await fetch(`${API_BASE}/auth/logout`, {
          method: "POST",
          headers: getHeaders(false),
          // credentials: 'include',
        });
      } catch (e) {
        // ignore network errors on logout
      }
    },
  },

  user: {
    getProfile: async (userId: number) => {
      const response = await fetch(`${API_BASE}/profile/${userId}`, {
        headers: getHeaders(),
        // credentials: 'include',
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
      console.log("🔍 GET_MY_FOODS called with donorId:", donorId);
      const response = await fetch(`${API_BASE}/food/my/${donorId}`, {
        headers: getHeaders(),
      });
      const data = await handleResponse(response);
      console.log("🔍 GET_MY_FOODS response:", data);
  
      // Map backend fields to frontend interface
      return data.map((item: any) => ({
        id: item.food_id,  // Map food_id → id
        donor_id: item.donor_id,
        food_name: item.food_name,
        quantity: item.quantity,
        expiry_date: item.expiry_date,
        status: item.status || 'available'
      }));
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
      console.log("🔍 GET_NEARBY_REQUESTS called");
      const response = await fetch(`${API_BASE}/food/requests/nearby`, {
        headers: getHeaders(),
      });
      const data = await handleResponse(response);
      console.log("🔍 GET_NEARBY_REQUESTS response:", data);
  
      // Map backend fields to frontend interface
      return data.map((item: any) => ({
        id: item.request_id,  // Map request_id → id
        receiver_id: item.receiver_id,
        food_type: item.food_type,
        quantity: item.quantity,
        urgency_level: item.urgency_level,
        deadline: item.deadline,
        status: item.status || 'pending'
      }));
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

  // MongoDB Features - ADD THIS SECTION
  mongodb: {
    // Activities
    getActivities: async (limit: number = 5) => {
      const response = await fetch(`${API_BASE}/logs/activities?limit=${limit}`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },
    
    // Analytics
    getAnalytics: async () => {
      const response = await fetch(`${API_BASE}/api/analytics/summary`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },
    
    // Route Optimization
    optimizeRoute: async (data: {
      pickup_points: Array<[number, number, number, string]>;
      delivery_points: Array<[number, number, number, string]>;
    }) => {
      const response = await fetch(`${API_BASE}/api/routes/optimize`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },
    
    // Food Images
    getFoodImages: async (foodId: number) => {
      const response = await fetch(`${API_BASE}/api/food/${foodId}/images`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },
    
    uploadFoodImage: async (foodId: number, formData: FormData) => {
      const headers = getHeaders(false);
      delete headers['Content-Type']; // Let browser set multipart boundary
      
      const response = await fetch(`${API_BASE}/api/food/${foodId}/images`, {
        method: "POST",
        headers,
        body: formData,
      });
      return handleResponse(response);
    },
    
    // Food Notes
    getFoodNotes: async (foodId: number) => {
      const response = await fetch(`${API_BASE}/api/notes/food/${foodId}`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },
    
    addFoodNote: async (foodId: number, data: {
      note_type: string;
      content: string;
      metadata: { priority: 'high' | 'medium' | 'low' };
    }) => {
      const response = await fetch(`${API_BASE}/api/notes/food/${foodId}`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    },
    
    // Feedback
    getFeedbackHistory: async (userId: number) => {
      const response = await fetch(`${API_BASE}/api/feedback/user/${userId}`, {
        headers: getHeaders(),
      });
      return handleResponse(response);
    },
  },
};

console.log("API BASE FROM api.ts =", API_BASE);
