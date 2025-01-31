import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  TextField,
  Grid,
  Card,
  CardContent,
  Rating,
  Button,
  List,
  ListItem,
  ListItemText,
  Box,
  CircularProgress,
} from '@mui/material';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [userRatings, setUserRatings] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Search for shows
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_BASE_URL}/shows/search?q=${searchQuery}`);
      setSearchResults(response.data.shows || []);
    } catch (err) {
      setError('Error searching for shows');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Handle rating changes
  const handleRatingChange = (showId, newValue) => {
    setUserRatings(prev => ({
      ...prev,
      [showId]: newValue
    }));
  };

  // Get recommendations based on ratings
  const getRecommendations = async () => {
    if (Object.keys(userRatings).length === 0) {
      setError('Please rate some shows first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/recommendations`, {
        ratings: userRatings,
        n: 5
      });
      setRecommendations(response.data.recommendations || []);
    } catch (err) {
      setError('Error getting recommendations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        TV Show Recommender
      </Typography>

      {/* Search Section */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={9}>
            <TextField
              fullWidth
              label="Search TV Shows"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={3}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              disabled={loading}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Search Results
          </Typography>
          <Grid container spacing={2}>
            {searchResults.map((show) => (
              <Grid item xs={12} sm={6} key={show.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{show.title}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Rating: {show.rating}
                    </Typography>
                    <Rating
                      value={userRatings[show.id] || 0}
                      onChange={(event, newValue) => {
                        handleRatingChange(show.id, newValue);
                      }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Get Recommendations Button */}
      <Box sx={{ mb: 4 }}>
        <Button
          variant="contained"
          onClick={getRecommendations}
          disabled={loading || Object.keys(userRatings).length === 0}
        >
          Get Recommendations
        </Button>
      </Box>

      {/* Error Message */}
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {/* Loading Indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Recommended Shows
          </Typography>
          <List>
            {recommendations.map((show) => (
              <ListItem key={show.id}>
                <ListItemText
                  primary={show.title}
                  secondary={`Predicted Rating: ${show.predicted_rating.toFixed(1)} / 5`}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Container>
  );
}

export default App; 