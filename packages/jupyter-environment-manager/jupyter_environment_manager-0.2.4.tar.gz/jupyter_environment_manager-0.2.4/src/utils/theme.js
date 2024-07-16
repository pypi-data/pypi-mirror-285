import { createTheme } from '@mui/material/styles';

const lightThemeStyle = {
  palette: {
    mode: 'light',
    primary: {
      main: '#d30982' // pink
    },
    secondary: {
      main: '#673ab7', // violet
      contrastText: '#ffffff'
    },
    secondaryHighlight: {
      main: '#562944', // dark violet
      contrastText: '#ffffff'
    },
    typography: {
      fontFamily: ['var(--jp-ui-font-family)'].join(',')
    },
    background: {
      alternate: 'linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%)'
    }
  },
  components: {
    MuiButton: {
      variants: [
        {
          props: { variant: 'slide' },
          style: {
            height: 'auto',
            textTransform: 'capitalize',
            fontSize: 14,
            fontWeight: 400,
            border: 'none',
            color: 'white',
            backgroundImage: 'linear-gradient(110deg,#B767FF 50%,#673ab7 50%)',
            backgroundSize: '222%',
            backgroundPosition: 'right',
            transition:
              'background-position 200ms linear, letter-spacing 200ms linear',
            ':hover': {
              backgroundPosition: 'left'
            }
          }
        },
        {
          props: { variant: 'slide', type: 'success' },
          style: {
            backgroundImage: 'linear-gradient(110deg,#8AB73A 50%,#673ab7 50%)'
          }
        },
        {
          props: { variant: 'slide', type: 'decline' },
          style: {
            border: '1px solid #d32f2f',
            color: '#d32f2f',
            backgroundImage:
              'linear-gradient(110deg, #e03333 50%,transparent 50%)',
            ':hover': {
              color: 'white'
            }
          }
        }
      ]
    }
  }
};

const darkThemeStyle = {
  ...lightThemeStyle,
  palette: {
    mode: 'dark',
    primary: {
      main: '#d30982'
    },
    secondary: {
      main: '#673ab7',
      contrastText: '#ffffff'
    },
    secondaryHighlight: {
      main: '#562944',
      contrastText: '#ffffff'
    },
    typography: {
      fontFamily: ['var(--jp-ui-font-family)'].join(',')
    },
    background: {
      alternate: '#1e1e1e'
    }
  }
};

export const lightTheme = createTheme(lightThemeStyle);
export const darkTheme = createTheme(darkThemeStyle);
