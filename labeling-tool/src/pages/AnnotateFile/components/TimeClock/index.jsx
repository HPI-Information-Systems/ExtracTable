import { Box, Paper, Typography } from '@material-ui/core';
import { HourglassEmptyOutlined, TimerOutlined } from '@material-ui/icons';
import { map, reduce } from 'lodash';
import moment from 'moment';
import React, { useEffect, useState } from 'react';
import theme from '../../../../theme';

const getElapsedTime = (startTime, endTime = moment()) => moment.duration(endTime.diff(startTime));
const getTotalTime = (timeClock, startTime) => {
  const durations = map(timeClock, ({ start, end }) => getElapsedTime(moment(start), moment(end)));
  return reduce(durations, (total, duration) => total.add(duration), getElapsedTime(startTime));
};

const TimeClock = ({ startTime, timeClock }) => {
  const [sessionTime, setSessionTime] = useState(getElapsedTime().humanize());
  const [totalTime, setTotalTime] = useState(getTotalTime(timeClock, startTime).humanize());
  useEffect(() => {
    const interval = setInterval(() => {
      setSessionTime(getElapsedTime(startTime).humanize());
      setTotalTime(getTotalTime(timeClock, startTime).humanize());
    }, 500);
    return () => clearInterval(interval);
  }, [startTime, timeClock]);
  return (
    <div className="TimeClock">
      <Paper variant="outlined" style={{ borderColor: theme.palette.primary.main }}>
        <Box display="flex" p={2}>
          <Box flexGrow={1} display="flex" alignItems="center">
            <TimerOutlined color="inherit" fontSize="inherit" />
            <Typography variant="body2">{ sessionTime }</Typography>
          </Box>
          <Box flexGrow={1} display="flex" alignItems="center">
            <HourglassEmptyOutlined color="inherit" fontSize="inherit" />
            <Typography variant="body2">{ totalTime }</Typography>
          </Box>
        </Box>
      </Paper>
    </div>
  );
};

export default TimeClock;
