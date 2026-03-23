const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Token ${token}` } : {};
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      const isJson = contentType && contentType.includes('application/json');
      
      if (!response.ok) {
        if (isJson) {
          const data = await response.json();
          throw { status: response.status, data };
        } else {
          // Server returned HTML error page
          throw { 
            status: response.status, 
            data: { error: `Server error (${response.status})` }
          };
        }
      }

      return isJson ? await response.json() : {};
    } catch (error) {
      // If error is already formatted, throw it
      if (error.status) {
        throw error;
      }
      // Network or other errors
      throw { 
        status: 0, 
        data: { error: error.message || 'Network error' }
      };
    }
  }

  // Auth endpoints
  async register(userData) {
    return this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({
        username: userData.username,
        email: userData.email,
        password: userData.password,
        password_confirm: userData.confirmPassword,
      }),
    });
  }

  async login(credentials) {
    return this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({
        username_or_email: credentials.email,
        password: credentials.password,
      }),
    });
  }

  async logout() {
    return this.request('/auth/logout/', {
      method: 'POST',
    });
  }

  // User endpoints
  async getCurrentUser() {
    return this.request('/users/me/');
  }

  async getUserByUsername(username) {
    return this.request(`/users/username/${username}/`);
  }

  async updateProfile(data) {
    return this.request('/users/me/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async toggleInvisibleMode(isInvisible) {
    return this.request('/users/me/', {
      method: 'PATCH',
      body: JSON.stringify({ is_invisible: isInvisible }),
    });
  }

  async getUserStats(userId) {
    return this.request(`/profiles/${userId}/stats/`);
  }

  // Upload endpoints
  async uploadAvatar(file) {
    const formData = new FormData();
    formData.append('avatar', file);

    const url = `${this.baseURL}/me/upload-avatar/`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...this.getAuthHeader(),
      },
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw { status: response.status, data };
    }
    return data;
  }

  async uploadBanner(file) {
    const formData = new FormData();
    formData.append('banner', file);

    const url = `${this.baseURL}/me/upload-banner/`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...this.getAuthHeader(),
      },
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw { status: response.status, data };
    }
    return data;
  }

  async deleteAvatar() {
    return this.request('/me/delete-avatar/', {
      method: 'DELETE',
    });
  }

  async deleteBanner() {
    return this.request('/me/delete-banner/', {
      method: 'DELETE',
    });
  }

  // Teams endpoints
  async getTeams(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/teams/${queryString ? `?${queryString}` : ''}`);
  }

  async getMyTeams() {
    return this.request('/teams/my_teams/');
  }

  async getUserTeams(username) {
    return this.request(`/teams/user/${username}/`);
  }

  async getTeam(id) {
    return this.request(`/teams/${id}/`);
  }

  async getTeamMembers(teamId) {
    return this.request(`/teams/${teamId}/members/`);
  }

  async removeMember(teamId, userId) {
    return this.request(`/teams/${teamId}/remove-member/`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  async invitePlayer(teamId, userId) {
    return this.request(`/teams/${teamId}/invite/`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  async searchUsers(query) {
    return this.request(`/users/?search=${encodeURIComponent(query)}`);
  }

  async createTeam(teamData) {
    return this.request('/teams/', {
      method: 'POST',
      body: JSON.stringify(teamData),
    });
  }

  async updateTeam(id, teamData) {
    return this.request(`/teams/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(teamData),
    });
  }

  async deleteTeam(id) {
    return this.request(`/teams/${id}/`, {
      method: 'DELETE',
    });
  }

  async getTeamStats(id) {
    return this.request(`/teams/${id}/stats/`);
  }

  async uploadTeamLogo(teamId, file) {
    const formData = new FormData();
    formData.append('logo', file);

    const url = `${this.baseURL}/teams/${teamId}/upload-logo/`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...this.getAuthHeader(),
      },
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw { status: response.status, data };
    }
    return data;
  }

  async uploadTeamBanner(teamId, file) {
    const formData = new FormData();
    formData.append('banner', file);

    const url = `${this.baseURL}/teams/${teamId}/upload-banner/`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...this.getAuthHeader(),
      },
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw { status: response.status, data };
    }
    return data;
  }

  // Games endpoints
  async searchGames(query) {
    return this.request(`/games/search/?query=${encodeURIComponent(query)}`);
  }

  async getGames(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/games/${queryString ? `?${queryString}` : ''}`);
  }

  // Tournaments endpoints (placeholder)
  async getTournaments(params = {}) {
    // TODO: Implement when tournaments API is ready
    return { results: [], count: 0 };
  }

  async getTournament(id) {
    // TODO: Implement when tournaments API is ready
    return null;
  }

  // Friends endpoints
  async getFriends() {
    return this.request('/friends/');
  }

  async getFriendRequests() {
    return this.request('/friends/requests/');
  }

  async getSentRequests() {
    return this.request('/friends/sent_requests/');
  }

  async sendFriendRequest(toUsername) {
    return this.request('/friends/send_request/', {
      method: 'POST',
      body: JSON.stringify({ to_username: toUsername }),
    });
  }

  async acceptFriendRequest(requestId) {
    return this.request('/friends/accept_request/', {
      method: 'POST',
      body: JSON.stringify({ request_id: requestId }),
    });
  }

  async declineFriendRequest(requestId) {
    return this.request('/friends/decline_request/', {
      method: 'POST',
      body: JSON.stringify({ request_id: requestId }),
    });
  }

  async cancelFriendRequest(requestId) {
    return this.request(`/friends/${requestId}/cancel_request/`, {
      method: 'DELETE',
    });
  }

  async removeFriend(username) {
    return this.request(`/friends/${username}/remove/`, {
      method: 'DELETE',
    });
  }

  // Notifications endpoints
  async getNotifications(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/notifications/${queryString ? `?${queryString}` : ''}`);
  }

  async markNotificationAsRead(notificationId) {
    return this.request(`/notifications/${notificationId}/mark_as_read/`, {
      method: 'POST',
    });
  }

  async markAllNotificationsAsRead() {
    return this.request('/notifications/mark_all_as_read/', {
      method: 'POST',
    });
  }

  async deleteNotification(notificationId) {
    return this.request(`/notifications/${notificationId}/`, {
      method: 'DELETE',
    });
  }

  async getUnreadCount() {
    return this.request('/notifications/unread_count/');
  }
}

export default new ApiService();
