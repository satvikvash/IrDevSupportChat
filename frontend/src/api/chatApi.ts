export interface ChatApiResponse {
  message: string;
  timestamp: Date;
}

export const sendMessage = async (message: string, history: any): Promise<ChatApiResponse> => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/testMessage', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, history }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const data = await response.json();

    return {
      message: data.message,
      timestamp: new Date(data.timestamp),
    };
  } catch (error) {
    console.error('Error sending message:', error);
    return {
      message: 'Something went wrong. Please try again later.',
      timestamp: new Date(),
    };
  }
};


export const login = async (username: string, password: string): Promise<{ success: boolean; error?: string }> => {
  // Simulate API latency
  await new Promise((resolve) => setTimeout(resolve, 1000))

  // For this mock, accept any non-empty credentials
  if (username.trim() && password.trim()) {
    return { success: true }
  }

  return {
    success: false,
    error: "Invalid username or password",
  }
}
