import { Message, CallMetadata } from './Interfaces'

const BASE_URL = `${process.env.REACT_APP_API_URL || "http://localhost:8000" }/calls`;

export const getCallMetadata = async (id: string): Promise<CallMetadata> => {
    const response = await fetch(`${BASE_URL}/metadata/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch metadata for ID ${id}`);
    }
    return response.json();
  };

export const getQuestionAnswer = async(callId: string,  question: string, conversationHistory: Message[]): Promise<string> => {
  const response = await fetch(`${BASE_URL}/ask-question/${callId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: question,
      conversation_history: conversationHistory
    }),
  }) 

  if (!response.ok) {
    throw new Error("Failed to fetch the response from the backend");
  }

  return response.json();

};

export const getCallIds = async (): Promise<string[]> => {
    const response = await fetch(`${BASE_URL}/ids`);
    if (!response.ok) {
      throw new Error('Failed to fetch call IDs');
    }
    return response.json();
  };