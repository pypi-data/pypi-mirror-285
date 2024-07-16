import React, { useEffect, useState } from 'react';
import {
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Skeleton,
  Typography
} from '@mui/material';
import { KeyboardArrowRight } from '@mui/icons-material';
import '../../style/Loading.css';

const MAX_WAITING_TIME = 3;

// The component shows a loader spinning wheel for the duration of MAX_WAITING_TIME
// After the duration, a "NO DATA FOUND" default message will appear.

const Loading = ({ timeOverMsg, timeOverDesc }) => {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    let interval;
    if (seconds < MAX_WAITING_TIME) {
      interval = setInterval(() => {
        setSeconds(seconds => seconds + 1);
      }, 1000);
    }
    return () => {
      clearInterval(interval);
    };
  }, [seconds]);

  if (seconds < MAX_WAITING_TIME) {
    return (
      <List sx={{ marginX: '8px' }}>
        {Array.from({ length: 10 }, (_, i) => i + 1).map(item => (
          <React.Fragment key={item}>
            <ListItem
              sx={{
                marginBottom: '8px',
                padding: '8px !important',
                backgroundColor: 'var(--jp-layout-color2)',
                borderRadius: '10px'
              }}
            >
              <ListItemAvatar sx={{ minWidth: '45px !important' }}>
                <Skeleton variant="circular" height="30px" width="30px" />
              </ListItemAvatar>
              <ListItemText>
                <Typography fontSize={16}>
                  <Skeleton variant="text" height="16px" width="180px" />
                </Typography>
              </ListItemText>
              <ListItemAvatar sx={{ minWidth: '30px' }} edge="end">
                <Skeleton variant="circular" height="30px" />
              </ListItemAvatar>
            </ListItem>
          </React.Fragment>
        ))}
      </List>
    );
  }

  return (
    <div className="env-lds-time-over">
      <h2>{timeOverMsg}</h2>
      <p>{timeOverDesc}</p>
    </div>
  );
};

Loading.defaultProps = {
  timeOverMsg: 'WORKSPACE EMPTY',
  timeOverDesc: 'Add or create an environment to get started!'
};

export default Loading;
