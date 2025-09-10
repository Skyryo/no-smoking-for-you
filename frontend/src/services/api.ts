import type { 
  SmokingHabitsRequest, 
  SmokingHabitsResponse, 
  SmokingHabitsError 
} from '../types/smokingHabits';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export class SmokingHabitsApiError extends Error {
  public errorResponse: SmokingHabitsError;

  constructor(errorResponse: SmokingHabitsError) {
    super(errorResponse.error.message);
    this.name = 'SmokingHabitsApiError';
    this.errorResponse = errorResponse;
  }
}

export class SmokingHabitsApi {
  async submitSmokingHabits(
    data: SmokingHabitsRequest,
    authToken?: string
  ): Promise<SmokingHabitsResponse> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${API_BASE_URL}/smoking-habits`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });

    const result = await response.json();
    
    if (!response.ok) {
      throw new SmokingHabitsApiError(result);
    }
    
    return result;
  }

  async getSmokingHabits(
    questionnaireId: string,
    authToken?: string
  ): Promise<SmokingHabitsResponse> {
    const headers: HeadersInit = {};

    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${API_BASE_URL}/smoking-habits/${questionnaireId}`, {
      method: 'GET',
      headers
    });

    const result = await response.json();
    
    if (!response.ok) {
      throw new SmokingHabitsApiError(result);
    }
    
    return result;
  }
}

// シングルトンインスタンス
export const smokingHabitsApi = new SmokingHabitsApi();
