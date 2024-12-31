import React, { useEffect, useState, useCallback } from 'react';
import { CallMetadata } from './Interfaces';
import { useNavigate } from 'react-router-dom';
import formatDuration from './Utils';
import { getCallMetadata, getCallIds } from './BackendApi';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Grid2,
  Divider
} from '@mui/material';

const CallsList: React.FC = () => {
  const [calls, setCalls] = useState<CallMetadata[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchAllCalls = useCallback(async () => {
    try {
      const ids = await getCallIds();
      const metadataPromises = ids.map(id => getCallMetadata(id));
      const metadataList = await Promise.all(metadataPromises);
      setCalls(metadataList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllCalls();
  }, [fetchAllCalls]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
        Pick a Call
      </Typography>

      <Divider sx={{ mb: 4 }} />

      <Grid2 container spacing={2}>
        {calls.map(call => (
          <Grid2 key={call.call_id} size={4}>
            <Card
              onClick={() => navigate(`/chat/${call.call_id}`, { state: call })}
              sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}
            >
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  {call.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {new Date(call.start_time).toLocaleString()}
                </Typography>
                <Typography variant="body2">
                  Duration: {formatDuration(call.duration)}
                </Typography>
              </CardContent>
            </Card>
          </Grid2>
        ))}
      </Grid2>
    </Box>
  );
};

export default CallsList;
