import { PersonOff } from '@mui/icons-material';
import { Box, Typography } from '@mui/material';
import React from 'react';

const UserNotFound = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      position="absolute"
      top="45%"
      left="35%"
    >
      <PersonOff color="disabled" sx={{ width: '64px', height: '64px' }} />
      <Typography color="InactiveCaptionText" sx={{ userSelect: 'none' }}>
        User not found
      </Typography>
    </Box>
  );
};

export default UserNotFound;
