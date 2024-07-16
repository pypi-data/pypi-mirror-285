import * as React from 'react';
import { styled } from '@mui/material/styles';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';

export const StyledAccordion = styled(props => (
  <MuiAccordion disableGutters elevation={0} square {...props} />
))(({ theme }) => ({
  border: 0,
  borderTop: '1px solid var(--jp-border-color0)',
  backgroundColor: 'var(--jp-layout-color1)',
  '&:not(:last-child)': {
    borderBottom: 0
  },
  '&:before': {
    display: 'none'
  }
}));

export const StyledAccordionSummary = styled(props => (
  <MuiAccordionSummary
    expandIcon={
      <ArrowRightIcon
        sx={{ fontSize: '1.5rem', color: 'var(--jp-layout-color4)' }}
      />
    }
    {...props}
  />
))(({ theme }) => ({
  flexDirection: 'row-reverse',
  '& .MuiAccordionSummary-expandIconWrapper.Mui-expanded': {
    transform: 'rotate(90deg)'
  },
  '& .MuiAccordionSummary-content': {
    margin: 0,
    marginLeft: '8px'
  },
  minHeight: '35px',
  padding: '0px 5px'
}));

export const StyledAccordionDetails = styled(MuiAccordionDetails)(
  ({ theme }) => ({
    padding: '0px 10px 10px 10px'
  })
);
