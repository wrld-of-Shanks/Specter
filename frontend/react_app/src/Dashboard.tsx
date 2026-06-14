import React, { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Person,
  ExitToApp,
  Dashboard as DashboardIcon,
  Gavel,
  Description,
  Message,
  AccountCircle,
  Settings,
  ArrowBack,
} from '@mui/icons-material';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_verified: boolean;
  created_at: string;
}

interface DashboardProps {
  user: User;
  onLogout: () => void;
  onNavigateHome: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ user, onLogout, onNavigateHome }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [stats] = useState({
    totalQueries: 0,
    documentsUploaded: 0,
    accountCreated: user.created_at,
  });

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    onLogout();
    handleMenuClose();
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: `
          linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.3)),
          url('./assets/hero.jpg') center/cover fixed no-repeat
        `,
        backdropFilter: 'blur(10px)',
        padding: 2,
      }}
    >
      <Container maxWidth="lg" sx={{ pt: 2, pb: 4 }}>
        {/* Back Button */}
        <Box mb={3}>
          <IconButton
            onClick={onNavigateHome}
            sx={{
              color: '#FFD700',
              backgroundColor: 'rgba(255, 215, 0, 0.1)',
              border: '1px solid rgba(255, 215, 0, 0.3)',
              '&:hover': {
                backgroundColor: 'rgba(255, 215, 0, 0.2)',
                transform: 'translateX(-2px)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            <ArrowBack />
          </IconButton>
        </Box>

        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography 
            variant="h4" 
            component="h1"
            sx={{
              color: '#FFD700',
              fontFamily: 'Roboto Condensed, sans-serif',
              fontWeight: 900,
              textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
            }}
          >
            Welcome back, {user.full_name}!
          </Typography>

        <Box>
          <IconButton onClick={handleMenuOpen} sx={{ p: 1 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <Person />
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleMenuClose}>
              <ListItemIcon>
                <AccountCircle fontSize="small" />
              </ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem onClick={handleMenuClose}>
              <ListItemIcon>
                <Settings fontSize="small" />
              </ListItemIcon>
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <ExitToApp fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Box>

        {/* User Info Card */}
        <Card 
          elevation={0}
          sx={{ 
            mb: 4,
            background: 'transparent !important',
            backgroundColor: 'transparent !important',
            backdropFilter: 'none',
            border: '2px solid rgba(255, 215, 0, 0.3)',
            borderRadius: 3,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.1)',
            '&:hover': {
              border: '2px solid rgba(255, 215, 0, 0.5)',
              boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)',
            },
            '& .MuiCardContent-root': {
              background: 'transparent !important',
              backgroundColor: 'transparent !important',
            },
          }}
        >
          <CardContent>
          <Box display="flex" alignItems="center" gap={3}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 64, height: 64 }}>
              <Person sx={{ fontSize: 32 }} />
            </Avatar>
            <Box>
              <Typography variant="h5" sx={{ color: '#fff' }}>{user.full_name}</Typography>
              <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {user.email}
              </Typography>
              <Box mt={1}>
                {user.role && (
                  <Chip
                    label={user.role.toUpperCase()}
                    color={user.role === 'admin' ? 'error' : 'primary'}
                    size="small"
                  />
                )}
                {user.is_verified && (
                  <Chip
                    label="Verified"
                    color="success"
                    size="small"
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
        gap: 3,
        mb: 4 
      }}>
        <Card
          elevation={0}
          sx={{
            background: 'transparent !important',
            backgroundColor: 'transparent !important',
            backdropFilter: 'none',
            '& .MuiCardContent-root': {
              background: 'transparent !important',
              backgroundColor: 'transparent !important',
            },
            border: '2px solid rgba(255, 215, 0, 0.4)',
            borderRadius: 3,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.12)',
            '&:hover': {
              border: '2px solid rgba(255, 215, 0, 0.6)',
              boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)',
              transform: 'translateY(-2px)',
              background: 'rgba(0, 0, 0, 0.25)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <CardContent sx={{ textAlign: 'center' }}>
            <Message color="primary" sx={{ fontSize: 48, mb: 1 }} />
            <Typography variant="h4" sx={{ color: '#fff', textShadow: '2px 2px 4px rgba(0,0,0,0.8)' }}>{stats.totalQueries}</Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
              Messages
            </Typography>
          </CardContent>
        </Card>

        <Card
          elevation={0}
          sx={{
            background: 'transparent !important',
            backgroundColor: 'transparent !important',
            backdropFilter: 'none',
            '& .MuiCardContent-root': {
              background: 'transparent !important',
              backgroundColor: 'transparent !important',
            },
            border: '2px solid rgba(255, 215, 0, 0.4)',
            borderRadius: 3,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.12)',
            '&:hover': {
              border: '2px solid rgba(255, 215, 0, 0.6)',
              boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)',
              transform: 'translateY(-2px)',
              background: 'rgba(0, 0, 0, 0.25)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <CardContent sx={{ textAlign: 'center' }}>
            <Description color="secondary" sx={{ fontSize: 48, mb: 1 }} />
            <Typography variant="h4" sx={{ color: '#fff', textShadow: '2px 2px 4px rgba(0,0,0,0.8)' }}>{stats.documentsUploaded}</Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
              Documents
            </Typography>
          </CardContent>
        </Card>

        <Card
          elevation={0}
          sx={{
            background: 'transparent !important',
            backgroundColor: 'transparent !important',
            backdropFilter: 'none',
            '& .MuiCardContent-root': {
              background: 'transparent !important',
              backgroundColor: 'transparent !important',
            },
            border: '2px solid rgba(255, 215, 0, 0.4)',
            borderRadius: 3,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.12)',
            '&:hover': {
              border: '2px solid rgba(255, 215, 0, 0.6)',
              boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)',
              transform: 'translateY(-2px)',
              background: 'rgba(0, 0, 0, 0.25)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <CardContent sx={{ textAlign: 'center' }}>
            <Gavel color="success" sx={{ fontSize: 48, mb: 1 }} />
            <Typography variant="h4" sx={{ color: '#fff', textShadow: '2px 2px 4px rgba(0,0,0,0.8)' }}>0</Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
              Cases
            </Typography>
          </CardContent>
        </Card>

        <Card
          elevation={0}
          sx={{
            background: 'transparent !important',
            backgroundColor: 'transparent !important',
            backdropFilter: 'none',
            '& .MuiCardContent-root': {
              background: 'transparent !important',
              backgroundColor: 'transparent !important',
            },
            border: '2px solid rgba(255, 215, 0, 0.4)',
            borderRadius: 3,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.12)',
            '&:hover': {
              border: '2px solid rgba(255, 215, 0, 0.6)',
              boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)',
              transform: 'translateY(-2px)',
              background: 'rgba(0, 0, 0, 0.25)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <CardContent sx={{ textAlign: 'center' }}>
            <DashboardIcon sx={{ fontSize: 48, mb: 1, color: '#FFD700', filter: 'drop-shadow(2px 2px 4px rgba(0,0,0,0.8))' }} />
            <Typography variant="h4" sx={{ color: '#fff', textShadow: '2px 2px 4px rgba(0,0,0,0.8)' }}>AI</Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
              Powered
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Quick Actions */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
        gap: 3 
      }}>
        <Card
          elevation={0}
          sx={{
            background: 'transparent !important',
            backgroundColor: 'transparent !important',
            backdropFilter: 'none',
            '& .MuiCardContent-root': {
              background: 'transparent !important',
              backgroundColor: 'transparent !important',
            },
            border: '2px solid rgba(255, 215, 0, 0.3)',
            borderRadius: 3,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.1)',
            '&:hover': {
              border: '2px solid rgba(255, 215, 0, 0.5)',
              boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ color: '#FFD700' }}>
              Quick Actions
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <Message color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Ask Legal Questions" 
                  sx={{ '& .MuiListItemText-primary': { color: '#fff' } }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Description color="secondary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Upload Documents" 
                  sx={{ '& .MuiListItemText-primary': { color: '#fff' } }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Gavel color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Legal Solutions" 
                  sx={{ '& .MuiListItemText-primary': { color: '#fff' } }}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        <Card
          elevation={0}
          sx={{
            background: 'transparent !important',
            backgroundColor: 'transparent !important',
            backdropFilter: 'none',
            '& .MuiCardContent-root': {
              background: 'transparent !important',
              backgroundColor: 'transparent !important',
            },
            border: '2px solid rgba(255, 215, 0, 0.3)',
            borderRadius: 3,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.1)',
            '&:hover': {
              border: '2px solid rgba(255, 215, 0, 0.5)',
              boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ color: '#FFD700' }}>
              Recent Activity
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Asked about cyber fraud penalties"
                  secondary="2 hours ago"
                  sx={{ 
                    '& .MuiListItemText-primary': { color: '#fff' },
                    '& .MuiListItemText-secondary': { color: 'rgba(255, 255, 255, 0.7)' }
                  }}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Uploaded legal document"
                  secondary="1 day ago"
                  sx={{ 
                    '& .MuiListItemText-primary': { color: '#fff' },
                    '& .MuiListItemText-secondary': { color: 'rgba(255, 255, 255, 0.7)' }
                  }}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Queried about theft laws"
                  secondary="3 days ago"
                  sx={{ 
                    '& .MuiListItemText-primary': { color: '#fff' },
                    '& .MuiListItemText-secondary': { color: 'rgba(255, 255, 255, 0.7)' }
                  }}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Box>

        {/* Account Information */}
        <Card 
          elevation={0}
          sx={{ 
            mt: 4,
            background: 'transparent !important',
            backgroundColor: 'transparent !important',
            backdropFilter: 'none',
            border: '2px solid rgba(255, 215, 0, 0.3)',
            borderRadius: 3,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.1)',
            '&:hover': {
              border: '2px solid rgba(255, 215, 0, 0.5)',
              boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)',
            },
            '& .MuiCardContent-root': {
              background: 'transparent !important',
              backgroundColor: 'transparent !important',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ color: '#FFD700' }}>
              Account Information
            </Typography>
            <Box display="flex" flexDirection="column" gap={2}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body1" sx={{ color: '#fff' }}>Account Created:</Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body1" sx={{ color: '#fff' }}>Email Verified:</Typography>
                <Chip
                  label={user.is_verified ? 'Verified' : 'Pending'}
                  color={user.is_verified ? 'success' : 'warning'}
                  size="small"
                />
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body1" sx={{ color: '#fff' }}>Account Type:</Typography>
                {user.role && (
                  <Chip
                    label={user.role.toUpperCase()}
                    color={user.role === 'admin' ? 'error' : 'primary'}
                    size="small"
                  />
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Dashboard;
