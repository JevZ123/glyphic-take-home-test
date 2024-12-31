import React, { useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { CallMetadata } from './Interfaces';
import formatDuration from './Utils';
import { getQuestionAnswer } from './BackendApi';
import {
  Box,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  CircularProgress,
  Card,
  CardContent,
  Divider,
} from '@mui/material';

const ChatPage: React.FC = () => {
  const { callId } = useParams<{ callId: string }>();
  const [userInput, setUserInput] = useState<string>("");
  const [conversation, setConversation] = useState<{ question: string; answer: string }[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [usePreviousChatMessages, setUsePreviousChatMessages] = useState<boolean>(false);
  const call = useLocation().state as CallMetadata;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const question = userInput.trim();
    setConversation([...conversation, { question, answer: "..." }]);

    setUserInput("");
    setLoading(true);

    try {
      const answer = await getQuestionAnswer(
        callId || "",
        question,
        usePreviousChatMessages
          ? conversation.flatMap((entry) => [
              { content: entry.question, role: "user" },
              { content: entry.answer, role: "assistant" },
            ])
          : []
      );

      setConversation((prev) =>
        prev.map((conv, idx) =>
          idx === prev.length - 1 ? { ...conv, answer } : conv
        )
      );
    } catch (error) {
      console.error(error);
      setConversation((prev) =>
        prev.map((conv, idx) =>
          idx === prev.length - 1
            ? { ...conv, answer: "No response" }
            : conv
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={4}>
      <Typography variant="h4" component="h1" gutterBottom textAlign="center">
        Type in your questions
      </Typography>

      <Divider sx={{ mb: 4 }} />
      
      <Card sx={{ mb: 4, p: 2 }}>
        <Typography variant="h5" gutterBottom>
          {call.title}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {new Date(call.start_time).toLocaleString()}
        </Typography>
        <Typography variant="body2">
          Duration: {formatDuration(call.duration)}
        </Typography>
      </Card>

      <FormControlLabel
        control={
          <Switch
            checked={usePreviousChatMessages}
            onChange={() => setUsePreviousChatMessages(!usePreviousChatMessages)}
          />
        }
        label="Use conversation history"
        sx={{ mb: 2 }}
      />

      <Box mb={4}>
        {conversation.map((entry, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="body1" color="textSecondary">
                <strong>User:</strong> {entry.question}
              </Typography>
              <Typography variant="body1">
                <strong>Assistant:</strong> {entry.answer}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      <form onSubmit={handleSubmit}>
        <Box display="flex" gap={2} alignItems="center" mb={2}>
          <TextField
            fullWidth
            variant="outlined"
            label="Type your question..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            disabled={loading}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Send"}
          </Button>
        </Box>
      </form>
    </Box>
  );
};

export default ChatPage;
