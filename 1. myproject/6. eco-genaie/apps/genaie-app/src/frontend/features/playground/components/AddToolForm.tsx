import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Grid,
  Alert,
} from '@mui/material';
import { usePlayground } from '../hooks/usePlayground';

interface ToolFormData {
  name: string;
  description: string;
  endpoint: string;
  method: string;
  parameters: string;
}

const AddToolForm: React.FC = () => {
  const [formData, setFormData] = useState<ToolFormData>({
    name: '',
    description: '',
    endpoint: '',
    method: 'POST',
    parameters: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { addTool } = usePlayground();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      await addTool(formData);
      setSuccess('Tool added successfully!');
      setFormData({
        name: '',
        description: '',
        endpoint: '',
        method: 'POST',
        parameters: '',
      });
    } catch (err) {
      setError('Failed to add tool. Please try again.');
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Add New Tool
      </Typography>
      <Box component="form" onSubmit={handleSubmit}>
        <Box sx={{ display: 'grid', gap: 2 }}>
          <TextField
            required
            fullWidth
            label="Tool Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
          />
          <TextField
            required
            fullWidth
            label="Description"
            name="description"
            multiline
            rows={2}
            value={formData.description}
            onChange={handleChange}
          />
          <TextField
            required
            fullWidth
            label="Endpoint"
            name="endpoint"
            value={formData.endpoint}
            onChange={handleChange}
          />
          <TextField
            required
            fullWidth
            label="Method"
            name="method"
            value={formData.method}
            onChange={handleChange}
          />
          <TextField
            required
            fullWidth
            label="Parameters (JSON format)"
            name="parameters"
            multiline
            rows={4}
            value={formData.parameters}
            onChange={handleChange}
            helperText="Enter parameters in JSON format"
          />
        </Box>
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {success}
          </Alert>
        )}
        <Button
          type="submit"
          variant="contained"
          color="primary"
          sx={{ mt: 2 }}
        >
          Add Tool
        </Button>
      </Box>
    </Paper>
  );
};

export default AddToolForm; 