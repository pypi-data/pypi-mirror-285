import React from 'react';
import { Slider, sliderClasses, styled } from '@mui/material';

const StyledSlider = styled(Slider)(({ theme, ...props }) => ({
  color: theme.palette.primary.main,
  height: 5,
  marginBottom: 0,
  marginTop: 25,
  [`& .${sliderClasses.rail}`]: {
    // opacity: 0.5,
    // backgroundColor: theme.palette.secondary.main,
  },
  [`& .${sliderClasses.track}`]: {
    border: 'none',
    backgroundColor:
      props.color === 'error'
        ? theme.palette.error.main
        : theme.palette.success.main
  },
  [`& .${sliderClasses.thumb}`]: {
    display: 'none'
  },
  [`& .${sliderClasses.markLabel}`]: {
    top: '-20px',
    fontSize: 12,
    padding: '1px 8px',
    borderRadius: '4px',
    color: theme.palette.common.white,
    backgroundColor: theme.palette.text.disabled
  },
  [`& .${sliderClasses.markLabelActive}`]: {
    color: theme.palette.common.white,
    backgroundColor:
      props.color === 'error'
        ? theme.palette.error.main
        : theme.palette.success.main
  },
  [`& [data-index="0"].${sliderClasses.markLabel}`]: {
    left: '9%!important'
  },
  [`& [data-index="2"].${sliderClasses.markLabel}`]: {
    left: '94%!important'
  },
  [`& .${sliderClasses.mark}`]: {
    width: 10,
    height: 10,
    borderRadius: '100vw',
    backgroundColor: theme.palette.text.disabled,
    outlineColor: theme.palette.text.disabled,
    outlineWidth: '1px',
    outlineStyle: 'solid',
    outlineOffset: '4px'
  },
  [`& .${sliderClasses.markActive}`]: {
    backgroundColor:
      props.color === 'error'
        ? theme.palette.error.main
        : theme.palette.success.main,
    outlineColor:
      props.color === 'error'
        ? theme.palette.error.main
        : theme.palette.success.main
  }
}));

export default function PublishSlider({ env }) {
  const queuePosition = (visibility, reviewStatus) => {
    if (visibility === 'public' && reviewStatus === 'approved') {
      return 100;
    } else if (visibility === 'private' && reviewStatus === 'pending') {
      return 50;
    } else if (visibility === 'private' && reviewStatus === 'requested') {
      return 1;
    } else if (visibility === 'private' && reviewStatus === 'denied') {
      return 100;
    } else return 0;
  };

  const publishSliderLabels = [
    { label: 'Requested', value: 0 },
    { label: 'Under Review', value: 50 },
    {
      label: env?.reviewStatus === 'denied' ? 'Denied' : 'Published',
      value: 100
    }
  ];

  return (
    <StyledSlider
      valueLabelDisplay="off"
      defaultValue={queuePosition(env?.visibility, env?.reviewStatus)}
      step={33.33}
      color={env?.reviewStatus === 'denied' ? 'error' : 'success'}
      marks={publishSliderLabels}
      disabled
    />
  );
}
