/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
import React, { Fragment } from 'react';
import contextTypes from '../contextTypes';
import EnvironmentTile from './EnvironmentTile';
import EnvironmentEditor from './EnvironmentEditor';
import '../../style/EnvironmentsSidebar.css';
import UserIcon from '../assets/icons/UserIcon';
import BackIcon from '../assets/icons/BackIcon';
import DescriptionIcon from '../assets/icons/DescriptionIcon';
import LinkIcon from '../assets/icons/LinkIcon';
import CloseIcon from '../assets/icons/CloseIcon';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import RefreshIcon from '../assets/icons/RefreshIcon';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import DataSaverOnIcon from '@mui/icons-material/DataSaverOn';
import HttpsIcon from '@mui/icons-material/Https';

import {
  Avatar,
  Button,
  Box,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  FormControl,
  Grid,
  IconButton,
  InputAdornment,
  MenuItem,
  Select,
  Snackbar,
  Stack,
  TextField,
  ThemeProvider,
  Tooltip,
  Typography,
  FormControlLabel,
  Paper,
  Checkbox,
  InputBase
} from '@mui/material';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/theme-kuroir';
import 'ace-builds/src-noconflict/theme-terminal';
import {
  AddCircleOutline,
  FileUpload,
  FilterList,
  ReceiptLongOutlined,
  ReceiptLongTwoTone,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import { darkTheme, lightTheme } from '../utils/theme';
import Loading from './Loading';
import { ACCOUNT_URL, API_URL, buildHeaders } from '../actions/ApiActions';
import { LayoutRestorer } from '@jupyterlab/application';
import { showDialog } from '@jupyterlab/apputils';
import EndUserAgreement from './EndUserAgreement';
import {
  StyledAccordion,
  StyledAccordionDetails,
  StyledAccordionSummary
} from './MuiStyledComponents';
import UserNotFound from './UserNotFound';

const INSTALL_ENV_PERMS_NODE = 'qbraid.environments.install';
const CREATE_ENV_PERMS_NODE = 'qbraid.environments.create';
const SHARE_ENV_PERMS_NODE = 'qbraid.environments.share';
const CLONE_ENV_PERMS_NODE = 'qbraid.environments.clone';
const DISABLE_GPU_CHECK = 'qbraid-env-gpu-check-alert';
const DEFAULT_IMG = `https://qbraid-static.s3.amazonaws.com/logos/qbraid.png`;
const UPLOAD_SIZE_LIMIT = 500; // size of image set to the limit of 500KB
const filtersData = [
  {
    value: 'highest_to_lowest_priority',
    label: 'Most Relevant'
  },
  {
    value: 'newest_to_oldest',
    label: 'Most Recent'
  },
  {
    value: 'most_to_least_installed',
    label: 'Most Popular'
  },
  {
    value: 'alphabetically_a_z',
    label: 'Alphabetically (A-Z)'
  },
  {
    value: 'alphabetically_z_a',
    label: 'Alphabetically (Z-A)'
  }
];

const pythonStatic = [
  {
    value: 'py39',
    label: 'Python 3.9.18',
    isLocked: true
  },
  {
    value: 'py310',
    label: 'Python 3.10.13',
    isLocked: true
  },
  {
    value: 'py311',
    label: 'Python 3.11.7',
    isLocked: true
  },
  {
    value: 'py312',
    label: 'Python 3.12.1',
    isLocked: true
  }
];

function updatePythonVersions(props, pythonStatic) {
  const sysPythonVersion =
    props.flux.getStore('UserStore').getState().config?.pythonVersion ||
    pythonStatic[0].label;
  const pythonSequential = pythonStatic.map(element => {
    const elementVersionParts = element.label.match(/Python (\d+\.\d+)\./);
    const sysVersionParts = sysPythonVersion.match(/Python (\d+\.\d+)\./);

    if (
      elementVersionParts &&
      sysVersionParts &&
      elementVersionParts[1] === sysVersionParts[1]
    ) {
      return {
        ...element,
        label: sysPythonVersion, // Update to match the system Python version
        isLocked: false // Unlock this version
      };
    }

    return element;
  });

  return pythonSequential.reduce((acc, item, index) => {
    if (!item.isLocked && index > 0) {
      acc.unshift(item); // Move unlocked item to the front
    } else {
      acc.push(item); // Keep other items in their order
    }
    return acc;
  }, []);
}

var timer;
export default class EnvironmentsSidebar extends React.Component {
  static childContextTypes = contextTypes;

  getChildContext() {
    const { flux } = this.props;
    return {
      getActions: flux.getActions.bind(flux),
      getStore: flux.getStore.bind(flux),
      apiBaseUrl: flux.apiBaseUrl,
      jupyterlab: flux.jupyterlab
    };
  }

  constructor(props) {
    super(props);
    this.aceContainerRef = React.createRef(); // for ace-editor parent container
    this.aceRef = React.createRef(); // for ace-editor
    this.imageInputRef = React.createRef(); // for input when uploading image for new environment
    this.state = {
      progress: 0,
      tags: [],
      tagsInputText: '',
      togglesCount: 0,
      isClickedRefresh: false,
      installingEnvironment:
        props.flux.getStore('EnvironmentStore').getState()
          .installingEnvironment || null,
      environments:
        props.flux.getStore('EnvironmentStore').getState().environments || [], // all environments
      qbUser: props.flux.getStore('UserStore').getState() || {}, // user details
      pythonVersions: updatePythonVersions(props, pythonStatic),

      // component state
      browsing: false,
      filterQuery: '',
      filteredEnvironments: [],
      editing: false,
      editingNewEnvForm: false,
      newEnvCode: '',
      newEnvName: '',
      newEnvDescription: '',
      newEnvSlug: '',
      newEnvKernelName: '',
      newEnvShellPrompt: '',
      newEnvPythonVersion:
        props.flux.getStore('UserStore').getState().config?.pythonVersion ||
        pythonStatic[0].label,
      newEnvExpandAdvanced: false,
      newEnvFormHelperTexts: {
        newEnvName: '',
        newEnvCode: ''
      },
      selectedEnvironment: null,
      showNoPermsDialog: false,
      imageUploadBox: false,
      img: DEFAULT_IMG,
      imgFile: null,
      imgUploadError: { open: false, msg: '' },
      imgAsIpykernelLogo: false,
      popupOpen: false,
      popupMsg: { msg: '', type: '' },
      currentTheme: document
        ?.getElementsByTagName('BODY')[0]
        ?.getAttribute('data-jp-theme-name')
        ?.toLowerCase()
        ?.includes('dark')
        ? darkTheme
        : lightTheme,
      isDarkTheme: document
        ?.getElementsByTagName('BODY')[0]
        ?.getAttribute('data-jp-theme-name')
        ?.toLowerCase()
        ?.includes('dark')
        ? true
        : false,
      newCustomEnvId: null,
      refreshEnvData: false,
      makeNewEnv: false,
      timeToInstall: 0,
      showFilter: false,
      sortBy: 'highest_to_lowest_priority',
      tagFilter: false,
      packageProgress: 0,
      packageInstallingEnv: '', //currently package installing environment
      verifyLoading: { loading: false, envId: '' },
      intelPermissionModal: false,
      currentEnv: null,
      returnToMyenv: false, // determine return path from clone
      expandedEnvs: [], // array of envid, contains id for the last environment which has been expanded.
      noUser: props.flux.getStore('UserStore').getState()?.user ? false : true,
      packageLoading: false, // When "More..." is clicked, load packages and show loader as per this state
      containerWidth: 300, // For aceEditor width changes, affects only specific version of safari
      accessCodeInput: '',
      accessCodeInputVisible: false,
      accessCodeLoading: false
    };
  }

  componentDidMount() {
    this.props.flux
      .getStore('EnvironmentStore')
      .listen(this.handleUpdateEnvironments);

    // Gets the body element of Jupyter lab &
    // observes the attribute "data-jp-theme-name",
    // if the value of the attr changes, the callback function inside MutationObserver gets triggered
    // which then refreshes the theme variables associated with this extension
    let body = document.getElementsByTagName('BODY')[0];
    const observer = new MutationObserver(() => {
      if (
        body.getAttribute('data-jp-theme-name').toLowerCase().includes('dark')
      ) {
        this.setState({ currentTheme: darkTheme, isDarkTheme: true });
      } else {
        this.setState({ currentTheme: lightTheme, isDarkTheme: false });
      }
    });
    observer.observe(body, {
      attributesFilter: ['data-jp-theme-name'],
      attributeOldValue: true
    });

    this.setState({
      containerWidth: this.aceContainerRef?.current?.offsetWidth
    });
  }

  componentDidUpdate(prevProps, prevState) {
    if (
      this.aceContainerRef?.current?.offsetWidth !== this?.state?.containerWidth
    ) {
      this.resizeEditor();
      this.setState({
        containerWidth: this.aceContainerRef?.current?.offsetWidth
      });
    }
  }

  componentWillUnmount() {
    this.props.flux
      .getStore('EnvironmentStore')
      .unlisten(this.handleUpdateEnvironments);
  }

  resizeEditor = () => {
    this.aceRef?.current?.editor?.resize();
  };

  handleChangeCode = code => {
    this.setState({ newEnvCode: code }, () => {
      this.setState(pre => ({
        ...pre,
        newEnvFormHelperTexts: pre.newEnvCode.length
          ? {
              ...pre.newEnvFormHelperTexts,
              newEnvCode: ''
            }
          : pre.newEnvFormHelperTexts
      }));
    });
  };

  handleUpdateEnvironments = storeState => {
    this.setState({
      environments: storeState.environments,
      installingEnvironment: storeState.installingEnvironment
    });
  };

  handleOpenPopup = (popUpMsg, popUpType) => {
    this.setState({
      popupOpen: true,
      popupMsg: { msg: popUpMsg, type: popUpType }
    });
  };

  handlePopupClose = () => {
    this.setState({ popupOpen: false, popUpMsg: { msg: '', type: '' } });
  };

  highlightKernelSelector = active => {
    /*
     * responsible for highlighting the kernel name when a kernel gets activated
     * adds a new dialogue box underneath the kernel name
     */

    let timerOutId;
    let timerInterval;
    const activeEnvs = this.state.environments.filter(
      env => env.installed && env.active
    ); // gets the list of all active envs
    const { app } = this.props; // gets the current jupyter lab instance
    const currentWidget = app.shell.currentWidget; // gets the main area widget
    const widgetToolbarItems = currentWidget.toolbar.layout.widgets; // gets the toolbar present in main area widgets
    const kernelElement = widgetToolbarItems.filter(widget =>
      widget.node.classList.contains('jp-KernelName')
    )[0]; // gets the kernel element in the toolbar
    if (!kernelElement) return; // if notebook isn't open don't try to highlight
    try {
      const HTMLkernelElement = document.querySelector(
        '.lm-Widget.p-Widget.jp-KernelName.jp-Toolbar-item'
      ); // gets the kernel element in the toolbar which will allow us to insert new element
      if (active) {
        kernelElement.addClass('highlight-kernel');
        const para = document.createElement('p');
        const node = document.createTextNode('Change kernel');
        para.appendChild(node);
        para.setAttribute('id', 'kernel-change-text');
        para.setAttribute('class', 'pos-fixed-kernel_message');
        HTMLkernelElement.appendChild(para);

        timerInterval = setInterval(() => {
          // looks for any layout changes during the period of para being activated
          const leftStackWidth =
            document?.getElementById('jp-left-stack')?.offsetWidth || 0;
          const mainAreaWidget = currentWidget.node.offsetWidth;
          para.style.right = `calc(100vw - ${mainAreaWidget}px - ${leftStackWidth}px)`;
          para.style.opacity = 1;
        }, 500);

        timerOutId = setTimeout(() => {
          HTMLkernelElement.removeChild(para);
          clearInterval(timerInterval);
        }, 5000);
      } else if (!activeEnvs.length) {
        kernelElement.removeClass('highlight-kernel');
      }
    } catch (error) {
      console.log(`Can't highlight`, error);
      if (timerInterval) {
        clearInterval(timerInterval);
      }
    } finally {
      if (timerInterval) {
        setTimeout(() => {
          clearInterval(timerInterval);
        }, 5000);
      }
    }
  };

  handleCheckAndActivateEnv = async env => {
    // Intel terms model first time user activates environment.
    if (!env.active) {
      if (env.slug === 'intel_zr7hfq' || env.slug === 'intel_dk7c2g') {
        let { user } = this.props.flux.getStore('UserStore').getState();
        if (!user.metadata.acceptedIntelTerms) {
          this.setState({ intelPermissionModal: true, currentEnv: env });
          return;
        }
      }

      // Check if GPUs are available on the system and show warning dialog if not
      if (env?.tags?.includes('gpu')) {
        // this.setState({ verifyLoading: { loading: true, envId: env._id } });
        const isGPUAvailable = await this.props.flux
          .getActions('EnvironmentActions')
          .checkGPU({ delayed: false });

        const isGPUCheckDialogDisabled =
          localStorage.getItem(DISABLE_GPU_CHECK); // true | false, null, undefined

        if (!isGPUAvailable && !isGPUCheckDialogDisabled) {
          // dialog going to show only if GPU is available and GPU check dialog is not set disable
          const result = await this.showWarnDialog({
            withCheckbox: true,
            titleText: 'GPU is not configured in your system',
            bodyText: `Proceed to add kernel anyway?`,
            submitButtonText: 'Add',
            cancelButtonText: 'Cancel'
          });
          if (!result.button.accept) {
            return;
          } else if (result.button.accept && result.isChecked) {
            localStorage.setItem(DISABLE_GPU_CHECK, true);
          }
        }
      }
    }

    this.handleToggleActiveEnvironment(env);
  };

  handleToggleActiveEnvironment = env => {
    this.props.flux
      .getActions('EnvironmentActions')
      .toggleActive(env._id)
      .then(() => this.highlightKernelSelector(env.active))
      .catch(error => {
        if (typeof error === 'string' && error.length > 0) {
          alert(error);
        } else {
          alert(
            'Sorry, unable to add/remove kernel at this time. Please try again later.'
          );
        }
      });
  };

  handleChangeFilterQuery = e => {
    let filterQuery = e?.target?.value.trim();
    // todoo: generate filteredEnvironments
    this.setState(prev => ({
      filterQuery,
      filteredEnvironments: this.applyEnvironmentFilter(
        filterQuery,
        prev.environments,
        prev.tags
      )
    }));
  };

  applyEnvironmentFilter = (filterQuery, envs, tagsArray) =>
    envs.filter(env => {
      let parsedFilterQuery = filterQuery?.trim().toLowerCase();
      if (parsedFilterQuery && tagsArray.length > 0) {
        // filters the environments by checking with the tags input arrays
        if (
          ((env.displayName &&
            env.displayName.toLowerCase().indexOf(parsedFilterQuery) !== -1) ||
            (env.description &&
              env.description.toLowerCase().indexOf(parsedFilterQuery) !==
                -1)) &&
          tagsArray.every(item => env.tags.includes(item))
        ) {
          return true;
        }
        return false;
      } else if (parsedFilterQuery) {
        if (env.displayName.toLowerCase().indexOf(parsedFilterQuery) !== -1) {
          return true;
        }
        if (env.slug.toLowerCase().indexOf(parsedFilterQuery) !== -1) {
          return true;
        }
        if (
          env.description &&
          env.description.toLowerCase().indexOf(parsedFilterQuery) !== -1
        ) {
          return true;
        }
        return false;
      } else if (tagsArray.length > 0) {
        if (tagsArray.every(item => env.tags.includes(item))) {
          return true;
        }
        return false;
      } else {
        return false;
      }
    });

  pollStatusLocal = async () => {
    try {
      const data = await this.props.flux
        .getActions('EnvironmentActions')
        .pollStatusLocal();
      return data;
    } catch (err) {
      console.log(err);
      return this.handleFinishInstallFailure();
    }
  };

  handleInstallProgress = async installTimeSec => {
    let installTime = installTimeSec * 1000; // milisecond install time
    let totalIters = 50; // number of progress bar updates
    let DELAY = installTime / totalIters; // progress bar update interval
    let iteration = 0;
    timer = setInterval(() => {
      iteration++;
      // weighted / momentum-based progress update
      const weightedProgress = 100 * ((iteration / totalIters) ** 1.5 + 0.05);
      this.setState(
        {
          progress:
            this.state.progress <= 100 ? Math.min(weightedProgress, 100) : 100
        },
        () => {
          if (this.state.progress >= 90) {
            clearInterval(timer);
            this.pollStatusLocal().then(data => {
              if (data) {
                if (data.success === true) {
                  this.setState({ progress: 100 });
                  return this.handleFinishInstallSuccess();
                } else {
                  return this.handleFinishInstallFailure();
                }
              }
            });
          }
        }
      );
    }, DELAY);
  };

  handleInstallProgressStream = async (environmentId, userId) => {
    const requestUrl = `${API_URL}/environments/install-status/${environmentId}/${userId}`;
    var eventSource = new EventSource(requestUrl);

    eventSource.addEventListener('update', event => {
      const { progress, complete, success } = JSON.parse(event.data);
      const percent = progress
        ? Math.min(progress * 100, 96)
        : this.state.progress;
      this.setState({ progress: percent });
      if (complete) {
        eventSource.close();
        console.log('Connection closed');
        return Boolean(success) === true
          ? this.handleFinishInstallSuccess()
          : this.handleFinishInstallFailure();
      }
    });

    eventSource.addEventListener('error', event => {
      console.error('Install error', event);
      eventSource.close();
      return this.handleFinishInstallFailure();
    });

    eventSource.onerror = error => {
      console.log('Network error', error);
      eventSource.close();
      return this.handleFinishInstallFailure();
    };

    eventSource.onopen = () => {
      console.log('Connection opened');
    };
  };

  registerInstalled = async (env, _installTime) => {
    try {
      const installedEnvs = await this.props.flux
        .getActions('EnvironmentActions')
        .registerInstalled();
      const envNotInstalled =
        !installedEnvs ||
        installedEnvs.length === 0 ||
        !installedEnvs.some(e => e.slug === env.slug);
      const userId = this.state.qbUser.user._id;

      if (envNotInstalled || !userId) {
        alert(
          `Your environment ${env.displayName} could not be installed at this time.`
        );
        return;
      }

      this.handleOpenPopup('Installation started!', 'success');
      this.closeEnvironmentBrowser();
      return this.handleInstallProgressStream(env._id, userId);
    } catch (err) {
      alert(
        `Your environment ${env.displayName} could not be installed at this time.`
      );
    }
  };

  // Display dialog when inserting a code snippet into editor where GPU is not available
  showWarnDialog = async ({
    withCheckbox,
    cancelButtonText,
    submitButtonText,
    bodyText,
    titleText
  }) => {
    let dialogObject = {
      title: titleText,
      body: bodyText,
      buttons: [
        {
          iconLabel: '',
          label: cancelButtonText, // Button label
          caption: 'Cancel', // Button title
          className: 'env_dialog-btn_cancel', // Additional button CSS class
          accept: false, // Whether this button will discard or accept the dialog
          displayType: 'default' // applies 'default' or 'warn' styles
        },
        {
          iconLabel: '',
          label: submitButtonText, // Button label
          caption: 'Ok', // Button title
          className: 'env_dialog-btn_confirm', // Additional button CSS class
          accept: true, // Whether this button will discard or accept the dialog
          displayType: 'default' // applies 'default' or 'warn' styles
        }
      ]
    };
    if (withCheckbox) {
      dialogObject = {
        ...dialogObject,
        checkbox: {
          label: "Don't ask me again", // Checkbox label
          caption: 'Reminder', // Checkbox title
          className: 'gpu_warn_dialog-checkbox', // Additional checkbox CSS class
          checked: false // Default checkbox state
        }
      };
    }
    return showDialog(dialogObject);
  };

  handleOpenIntelPermissionModal = () => {
    this.setState({ intelPermissionModal: true });
  };

  handleCloseIntelPermissionModal = () => {
    this.setState({ intelPermissionModal: false });
  };

  handleAcceptTermsAndCondition = async () => {
    try {
      const response = await this.props.flux
        .getActions('EnvironmentActions')
        .acceptAgreement();
      if (response) {
        await this.props.flux.getActions('UserActions').getUser(); // updates user information
        this.handleToggleActiveEnvironment(this.state.currentEnv);
      }
    } catch (err) {
      console.log(err);
    } finally {
      this.handleCloseIntelPermissionModal();
    }
  };

  renderIntelTermsAndConditionModal = () => {
    return (
      <Dialog
        open={this.state.intelPermissionModal}
        onClose={() => this.handleCloseIntelPermissionModal()}
      >
        <Stack px="24px" pt="16px" gap={1} sx={{ userSelect: 'none' }}>
          <ReceiptLongOutlined
            fontSize="inherit"
            sx={theme => ({
              width: 48,
              height: 48,
              marginInline: 'auto',
              rotate: '25deg',
              color: theme.palette.secondary.light
            })}
          />
          <Divider>
            <Typography
              fontSize={22}
              textTransform="uppercase"
              fontWeight={600}
              sx={theme => ({
                WebkitTextFillColor: 'transparent',
                textFillColor: 'transparent',
                background: `linear-gradient( 45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main} )`,
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text'
              })}
            >
              End User Agreement Terms
            </Typography>
          </Divider>
          <Typography fontSize={16} textAlign="center" color="text.secondary">
            qBraid Customer
          </Typography>
        </Stack>
        <DialogContent sx={{ overflow: 'hidden' }}>
          <EndUserAgreement />
        </DialogContent>
        <DialogActions sx={{ gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            sx={{ borderRadius: '6px' }}
            onClick={() => this.handleCloseIntelPermissionModal()}
          >
            Decline
          </Button>
          <Button
            size="small"
            variant="contained"
            sx={{ borderRadius: '6px', background: 'rgb(103, 58, 183)' }}
            onClick={this.handleAcceptTermsAndCondition}
          >
            Accept
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  handleStartInstallEnvironment = env => {
    if (this.state.installingEnvironment) {
      // only allow one environment installation to execute at a time
      console.log('EnvSideBar Only Allow one install at a time');
      return;
    }

    // Block install button action for pre-installed environments
    const baseMsg =
      'The {} environment is available only from the {} Lab image.';
    const envDetails = {
      qsharp_b54crn: ['Microsoft Q#', '4vCPU+']
    };

    if (envDetails[env.slug]) {
      const [envName, tier] = envDetails[env.slug];
      return alert(baseMsg.replace('{}', envName).replace('{}', tier));
    }

    if (env.isPreInstalled) {
      return alert(
        'This environment comes pre-installed and is not available for installation via the Environment Manager. To access this environment, launch the appropriate qBraid Lab instance from the Computer Manager. If you believe you are seeing this message in error, please use the Help drop-down to report a bug.'
      );
    }

    // permissions check
    let { user } = this.props.flux.getStore('UserStore').getState();
    if (
      (!user ||
        !user.permissionsNodes ||
        user.permissionsNodes.indexOf(INSTALL_ENV_PERMS_NODE) === -1) &&
      !env.tags.includes('free')
    ) {
      return this.openNoPermsDialog();
    }
    this.installEnvironment(env);
  };

  installEnvironment = async env => {
    if (env?.tags?.includes('gpu')) {
      this.setState({ verifyLoading: { loading: true, envId: env._id } });
      const isGPUAvailable = await this.props.flux
        .getActions('EnvironmentActions')
        .checkGPU({ delayed: true });

      if (!isGPUAvailable) {
        this.setState({ verifyLoading: { loading: false, envId: '' } });
        const result = await this.showWarnDialog({
          withCheckbox: false,
          titleText: 'GPU is not configured in your system',
          bodyText: `Do you want to proceed?`,
          cancelButtonText: 'Cancel',
          submitButtonText: 'Install'
        });
        if (!result.button.accept) {
          return;
        }
      } else {
        this.setState({ verifyLoading: { loading: false, envId: '' } });
      }
    }
    try {
      const installTime = await this.props.flux
        .getActions('EnvironmentActions')
        .startInstall(env._id);
      if (installTime) {
        this.setState({ progress: 10, timeToInstall: installTime });
        this.registerInstalled(env, installTime);
      }
      if (env?.reviewStatus === 'requested') {
        let { user } = this.props.flux.getStore('UserStore').getState();
        if (user.email === 'contact@qbraid.com') {
          this.props.flux
            .getActions('EnvironmentActions')
            .updatePublishStatus(env.slug, 'pending');
        }
      }
    } catch (err) {
      console.log(`Error: ${err}`);
      return alert(
        'Your environment ' +
          env.displayName +
          ' could not be installed at this time.'
      );
    }
  };

  handleFinishInstallSuccess = () => {
    const env = this.state.installingEnvironment;
    if (!env) return;
    this.setState({ progress: 0, timeToInstall: 0 });
    this.resetNewEnvData();
    this.props.flux
      .getActions('EnvironmentActions')
      .registerInstallingNull()
      .then(data => {
        if (data !== true) return this.handleFinishInstallFailure();
        this.props.flux.getActions('EnvironmentActions').toggleActive(env._id);
      });
  };

  handleFinishInstallFailure = () => {
    const env = this.state.installingEnvironment;
    if (!env) return;
    this.setState({ progress: 0, timeToInstall: 0 });
    this.resetNewEnvData();
    this.props.flux
      .getActions('EnvironmentActions')
      .uninstall(env.slug)
      .then(_data => {
        this.props.flux
          .getActions('EnvironmentActions')
          .registerInstalled()
          .then(_installedEnvs => {
            this.handleOpenPopup('Installation Failure', 'error');
            return alert(
              'Your environment ' +
                env.displayName +
                ' could not be installed at this time.'
            );
          })
          .catch(err => {
            console.log(err);
            this.handleOpenPopup('Installation Failure', 'error');
            return alert(
              'Your environment ' +
                env.displayName +
                ' could not be installed at this time.'
            );
          });
      })
      .catch(err => {
        console.log(err);
        this.handleOpenPopup('Uninstallation Failure', 'error');
        return alert(
          'Your environment ' +
            env.displayName +
            ' could not be uninstalled at this time.'
        );
      });
  };

  handleRefreshEnvironments = ({ clickedRefresh }) => {
    if (clickedRefresh) {
      this.setState(prev => ({
        togglesCount: ++prev.togglesCount
      }));
    }
    if (this.state.noUser) return;
    if (clickedRefresh) this.setState({ isClickedRefresh: true });
    this.props.flux
      .getActions('EnvironmentActions')
      .updateAll()
      .then(res => {
        this.props.flux
          .getActions('EnvironmentActions')
          .registerInstalled()
          .then(_envs => {
            this.setState({ isClickedRefresh: false });
            if (
              this.state.installingEnvironment &&
              !this.state.packageInstallingEnv
            ) {
              const userId = this.state.qbUser.user._id;
              const envId = this.state.installingEnvironment._id;
              return this.handleInstallProgressStream(envId, userId);
              // return this.handleInstallProgress(60);
            }
          })
          .catch(err => {
            console.log(err);
            alert("Can't refresh the environment now, Please try again");
          });
      })
      .catch(err => {
        console.log(err);
        alert("Can't refresh the environment now, Please try again");
      });
  };

  handleNewEnvironmentClick = () => {
    // This is a handler for when the 'New Environment' button gets clicked
    // If the user has the correct permissions to create a new environment,
    // the environment form is opened. If not, a message is displayed
    // telling the user that they don't have the correct permissions.
    let { user } = this.props.flux.getStore('UserStore').getState();
    if (
      !user ||
      !user.permissionsNodes ||
      user.permissionsNodes.indexOf(CREATE_ENV_PERMS_NODE) === -1
    ) {
      return this.openNoPermsDialog();
    }
    return this.openNewEnvironmentForm();
  };

  handleAddPinned = environmentId => {
    this.props.flux
      .getActions('EnvironmentActions')
      .addPinned(environmentId)
      .catch(err => {
        console.log('addPinError : ', err);
        // alert('Unable to perform this operation, Please try again');
      });
  };

  handleRemovePinned = environmentId => {
    this.props.flux
      .getActions('EnvironmentActions')
      .removePinned(environmentId)
      .catch(err => {
        console.log('removePinError : ', err);
        // alert('Unable to perform this operation, Please try again');
      });
  };

  registerNewInstallEnv = async env => {
    try {
      await this.props.flux
        .getActions('EnvironmentActions')
        .registerInstalling(env._id);
      this.setState({ progress: 40 });

      // wait for python -m venv command to finish
      const pollData = await this.pollStatusLocal();
      if (pollData.success === true) {
        return this.handleInstallEnvPackages({
          slug: env.slug,
          packages: env.packagesInImage,
          upgradePip: true,
          systemSitePackages: true
        });
      } else {
        return this.handleFinishInstallFailure();
      }
    } catch (err) {
      console.log(err);
      return this.handleFinishInstallFailure();
    }
  };

  updateAllEnv = async () => {
    try {
      const data = await this.props.flux
        .getActions('EnvironmentActions')
        .updateAll();
      if (data) {
        const installedEnvs = await this.props.flux
          .getActions('EnvironmentActions')
          .registerInstalled();
        if (installedEnvs) {
          let newEnv = installedEnvs.find(
            e => e.slug === this.state.newEnvSlug
          );
          this.setState({ newCustomEnvId: newEnv._id });
          this.registerNewInstallEnv(newEnv);
        }
      }
    } catch (err) {
      console.log(err);
      return this.handleFinishInstallFailure();
    }
  };

  handleCreateEnvironmentClick = async () => {
    // This is a handler for when the 'Create' button is clicked
    // on the new environment form. It closes the form, and begins
    // the process of creating a new environment using the
    // information that the user entered in the form. This starts
    // with an API request that creates a unique 'slug' value. This
    // slug corresponds to the name of the directory in the user's
    // filesystem where the new python virtual environment was created,
    // i.e. /home/jovyan/.qbraid/environments/{slug}.
    if (this.state.newEnvName === '') {
      this.setState({
        newEnvFormHelperTexts: {
          ...this.state.newEnvFormHelperTexts,
          newEnvName: 'You must provide a name for the environment.'
        }
      });
      return;
    }
    this.setState({
      newEnvFormHelperTexts: {
        ...this.state.newEnvFormHelperTexts,
        newEnvName: ''
      }
    });
    // verify requirements.txt file
    // if (this.state.newEnvCode === '') {
    //   this.setState({
    //     newEnvFormHelperTexts: {
    //       ...this.state.newEnvFormHelperTexts,
    //       newEnvCode: 'Add some packages to create custom environment'
    //     }
    //   });
    //   return;
    // }
    this.setState({
      newEnvFormHelperTexts: {
        newEnvName: '',
        newEnvCode: ''
      }
    });
    this.setState({ makeNewEnv: true });
    let inutTagArray = [];
    if (this.state.tagsInputText !== '') {
      inutTagArray = this.state.tagsInputText?.split(',');
    }
    const tagArray = [...new Set([...this.state.tags, ...inutTagArray])];
    const envData = {
      name: this.state.newEnvName,
      description: this.state.newEnvDescription,
      code: this.state.newEnvCode,
      tags: tagArray,
      image: this.state.imgFile,
      kernelName: this.state.newEnvKernelName,
      prompt: this.state.newEnvShellPrompt
    };
    try {
      const qbraidData = await this.props.flux
        .getActions('EnvironmentActions')
        .createNewEnvironment(envData);
      if (qbraidData && qbraidData.slug) {
        this.handleOpenPopup('Installation started!', 'success');
        this.setState({ progress: 20 });
        this.setState({ newEnvSlug: qbraidData.slug });
        const status = await this.props.flux
          .getActions('EnvironmentActions')
          .createCustomEnv({
            slug: qbraidData.slug,
            kernelName: qbraidData.kernelName,
            prompt: qbraidData.prompt,
            image:
              this.state.imgFile && this.state.imgAsIpykernelLogo
                ? this.state.img
                : null
          });
        if (status !== 202) {
          // is this status check redundant?
          try {
            this.resetNewEnvData();
            this.props.flux.getActions('EnvironmentActions').uninstall(slug);
          } catch (err) {
            console.log(err);
          }
          throw new Error('Unable to create new environment');
        }
        this.updateAllEnv();
      }
    } catch (err) {
      console.log(err);
      this.handleOpenPopup(
        'Sorry, something went wrong: unable to create new environment. Please try again later.',
        'error'
      );
    }
    setTimeout(() => {
      this.closeNewEnvironmentForm();
      this.closeEnvironmentBrowser();
      this.handleResetImg();
      this.setState({ editingNewEnvForm: false, makeNewEnv: false });
    }, 3000);
  };

  handleInstallEnvPackages = async installData => {
    // This is a handler for pip installing packages into the
    // new environment. It takes an optional requirements.txt
    // package list entered by the user in the new environment form
    // along with the environment 'slug' i.e. virtual environment
    // directory name that was received from 'handleCreateEnvironmentClick',
    // and triggers an action to install the packages.
    try {
      const data = await this.props.flux
        .getActions('EnvironmentActions')
        .installPackagesPyvenv(installData);
      if (!data || (data.status !== 200 && data.status !== 202)) {
        return this.handleFinishInstallFailure();
      }
      this.setState({ progress: 60 });

      // wait for pip install command to finish
      const pollData = await this.pollStatusLocal();
      if (pollData.success !== true) {
        return this.handleFinishInstallFailure();
      }
      let env = this.state.installingEnvironment;

      // update local environment store with new packages list
      await this.props.flux
        .getActions('EnvironmentActions')
        .updatePackagesList(env._id);

      this.setState({ progress: 85 });

      // update mongoDB with new packages list
      await this.props.flux
        .getActions('EnvironmentActions')
        .updateCustomPackageListInMongoDB({
          slug: env.slug,
          packageList: env.packagesInImage
        });
      return this.handleFinishInstallSuccess();
    } catch (err) {
      console.log(err);
      return this.handleFinishInstallFailure();
    }
  };

  onToggleExpand = _id => {
    // let newEnvironment = this.state.environments.map(row => {
    //   let cloneItem = row;
    //   if (row._id === _id || row._id === this.state.newCustomEnvId) {
    //     cloneItem.isExpanded = cloneItem.isExpanded ? false : true;
    //   }
    //   return cloneItem;
    // });
    // this.setState({
    //   environments: newEnvironment,
    //   newCustomEnvId: null
    // });
    this.setState({ newCustomEnvId: null });
    if (this.state.expandedEnvs.includes(_id)) {
      this.setState(prev => {
        return {
          ...prev,
          expandedEnvs: prev.expandedEnvs.filter(envid => envid !== _id)
        };
      });
      return;
    }
    this.setState(prev => {
      return { ...prev, expandedEnvs: [...prev.expandedEnvs, _id] };
    });
  };

  onTogglePinned = _id => {
    let newEnvironment = this.state.environments.map(row => {
      let cloneItem = row;
      if (row._id === _id) {
        if (cloneItem.pinned) {
          this.handleRemovePinned(_id);
        } else {
          this.handleAddPinned(_id);
        }
        cloneItem.pinned = cloneItem.pinned ? false : true;
      }
      return cloneItem;
    });
    this.setState({
      environments: newEnvironment
    });
  };

  handleOpenEnvEditorInstalled = (env, installing) => {
    this.openEnvironmentEditor(env);
    // Don't update package list for envs that use base conda python
    if (env.slug !== 'qsharp_b54crn' && !installing) {
      this.setState({ packageLoading: true });
      this.props.flux
        .getActions('EnvironmentActions')
        .updateQuantumJobStatus(env.slug)
        .catch(err => {
          console.log('Error updating quantum job status:', err);
        });
      this.props.flux
        .getActions('EnvironmentActions')
        .updatePackagesList(env._id)
        .then(() => {
          this.setState({ packageLoading: false });
        })
        .catch(err => {
          console.log('Error updating package list:', err);
          this.setState({ packageLoading: false });
        });
    }
    return;
  };

  openImgUploadError = ({ open, msg }) => {
    this.setState({ imgUploadError: { open, msg } });
  };

  closeImgUploadError = () => {
    this.setState({ imgUploadError: { open: false, msg: '' } });
  };

  handleAddButton = () => {
    const envsMounted = this.state.qbUser.isMount;
    this.setState({ browsing: true });

    // if filesystem not mounted, add button takes
    // user directly to create new env form
    if (envsMounted !== true) {
      this.handleNewEnvironmentClick();
    }
  };

  closeEnvironmentBrowser = () => this.setState({ browsing: false });

  openEnvironmentEditor = env =>
    this.setState({ editing: true, selectedEnvironment: env });

  closeEnvironmentEditor = () =>
    this.setState({ editing: false, selectedEnvironment: null });

  openNewEnvironmentForm = () =>
    this.setState({
      filterQuery: '',
      filteredEnvironments: [],
      tags: [],
      tagsInputText: '',
      editingNewEnvForm: true,
      tagFilter: false,
      newEnvExpandAdvanced: false,
      newEnvFormHelperTexts: {
        newEnvName: '',
        newEnvCode: ''
      }
    });
  cloneEnvironment = env => {
    // permissions check
    let { user } = this.props.flux.getStore('UserStore').getState();
    if (
      !user ||
      !user.permissionsNodes ||
      user.permissionsNodes.indexOf(CLONE_ENV_PERMS_NODE) === -1 ||
      (!env.installed &&
        !env.tags.includes('free') &&
        user.permissionsNodes.indexOf(INSTALL_ENV_PERMS_NODE) === -1)
    ) {
      return this.openNoPermsDialog();
    }

    const newEnvBaseName = env.displayName.includes('(Copy)')
      ? env.displayName.substr(0, env.displayName.lastIndexOf(' '))
      : env.displayName;
    const dupEnvCount = this.state.environments.filter(
      element =>
        element.displayName.includes(newEnvBaseName) &&
        element.slug !== env.slug
    ).length;
    this.setState({
      returnToMyenv: !this.state.browsing && true,
      browsing: true,
      newEnvName: `${newEnvBaseName} (Copy)${
        dupEnvCount > 0 ? ` (${dupEnvCount})` : ''
      }`,
      newEnvDescription: env.description,
      tags: [...env.tags].filter(item => item !== 'custom'),
      newEnvCode: env?.packagesInImage
        ? [...env?.packagesInImage].join('\n')
        : '',
      img: env?.logo?.light ?? DEFAULT_IMG,
      filterQuery: '',
      filteredEnvironments: [],
      editingNewEnvForm: true,
      tagFilter: false
    });
  };

  closeNewEnvironmentForm = () => {
    const envsMounted = this.state.qbUser.isMount;
    // const notInstalledEnvs = this.state.environments.filter(
    //   env => !env.installed
    // );

    // if (_.isEmpty(notInstalledEnvs)) {
    if (envsMounted !== true) {
      this.setState({ browsing: false });
    } else {
      this.setState({ browsing: this.state.returnToMyenv ? false : true });
    }

    this.setState({
      returnToMyenv: false,
      editingNewEnvForm: false,
      newEnvDescription: '',
      newEnvName: '',
      tags: [],
      tagsInputText: '',
      img: DEFAULT_IMG,
      newEnvCode: '',
      filterQuery: '',
      filteredEnvironments: [],
      tagFilter: false
    });
  };

  resetNewEnvData = () =>
    // This is a function for reseting all the state values
    // that are set when a new environment is created. In
    // the end, it may not be needed.
    this.setState({
      newEnvCode: '',
      newEnvName: '',
      newEnvDescription: '',
      newEnvSlug: '',
      newEnvKernelName: '',
      newEnvShellPrompt: '',
      tags: [],
      tagsInputText: '',
      tagFilter: false
    });

  openNoPermsDialog = () => this.setState({ showNoPermsDialog: true });

  closeNoPermsDialog = () => this.setState({ showNoPermsDialog: false });

  handleChangeTags = e => {
    this.setState({
      tagsInputText: e.target.value
    });
  };

  handleAddChips = event => {
    event.preventDefault();
    if (!this.state.tagsInputText) {
      return;
    }
    // the python versions are added as tags, from python version drop down
    // so if the user tries to add them in, prevent that tag for python version
    if (
      this.state.pythonVersions
        .map(item => item.value)
        .includes(this.state.tagsInputText)
    ) {
      return;
    }
    const tagArrayTemp = [
      ...new Set([...this.state.tags, this.state.tagsInputText])
    ];
    this.setState(prev => ({
      tagFilter: prev.browsing && !prev.editingNewEnvForm ? true : false,
      tags: tagArrayTemp,
      tagsInputText: '',
      filteredEnvironments:
        prev.browsing && !prev.editingNewEnvForm
          ? this.applyEnvironmentFilter(
              prev.filterQuery,
              prev.environments,
              tagArrayTemp
            )
          : []
    }));
  };

  handleDeleteChips = items => () => {
    const filterdTagsArray = this.state.tags.filter(chip => chip !== items);
    const filterStatus = filterdTagsArray.length === 0 ? false : true;

    this.setState(prev => ({
      tagFilter:
        prev.browsing && !prev.editingNewEnvForm ? filterStatus : false,
      tags: filterdTagsArray,
      filteredEnvironments:
        prev.browsing && !prev.editingNewEnvForm
          ? this.applyEnvironmentFilter(
              prev.filterQuery,
              prev.environments,
              filterdTagsArray
            )
          : []
    }));
  };
  handlePythonVersionChange = label => {
    const tagArrayTemp = [
      ...new Set(
        [
          ...this.state.tags,
          this.state.pythonVersions.filter(item => item.label === label)[0]
            .value
        ].filter(item => {
          if (
            !this.state.pythonVersions
              .filter(pyItem => pyItem.label !== label)
              .map(item => item.value)
              .includes(item)
          ) {
            return item;
          }
        })
      )
    ];
    this.setState({ tags: tagArrayTemp });
  };

  handleImageUploadBoxClose = () => {
    this.setState({
      imageUploadBox: false
    });
    if (this.state.img !== DEFAULT_IMG) {
      localStorage.setItem(this.state.newEnvName, this.state.img);
    }
    this.closeImgUploadError();
  };

  handleImageUploadBoxOpen = () => {
    this.setState({ imageUploadBox: true });
  };

  handleImageUpload = e => {
    const reader = new FileReader();
    const file = e.target.files[0];

    // Check if the file size exceeds the limit
    if (file.size > UPLOAD_SIZE_LIMIT * 1024) {
      this.openImgUploadError({
        msg: `File size exceeded limit ${UPLOAD_SIZE_LIMIT}KB`,
        open: true
      });
      return;
    }

    // Check if the file is a PNG
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (fileExtension !== 'png') {
      this.openImgUploadError({
        msg: 'Only PNG files are allowed',
        open: true
      });
      return;
    }

    reader.readAsDataURL(file);

    // Check if the image is square
    reader.onload = event => {
      const img = new Image();
      img.onload = () => {
        if (img.width !== img.height) {
          this.openImgUploadError({
            msg: 'The image must be square',
            open: true
          });
        } else {
          this.setState({
            img: event.target.result,
            imgFile: file
          });
          this.closeImgUploadError();
        }
      };
      img.src = event.target.result;
    };
  };

  handleUseAsIpykernelLogoChange = () => {
    this.setState(prev => ({
      imgAsIpykernelLogo: !prev.imgAsIpykernelLogo
    }));
  };

  handleResetImg = () => {
    this.setState(
      {
        img: DEFAULT_IMG,
        imgFile: DEFAULT_IMG,
        imgAsIpykernelLogo: false
      },
      () => {
        if (this.imageInputRef?.current) {
          this.imageInputRef.current.value = '';
        }
      }
    );
  };

  compareEnvs = (a, b) => {
    // Handle pinned environments first
    if (a.pinned || b.pinned) {
      return !a.pinned - !b.pinned;
    }

    let result;

    switch (this.state.sortBy) {
      case 'alphabetically_a_z':
        result = a.displayName
          .toLowerCase()
          .localeCompare(b.displayName.toLowerCase());
        break;
      case 'alphabetically_z_a':
        result = b.displayName
          .toLowerCase()
          .localeCompare(a.displayName.toLowerCase());
        break;
      case 'most_to_least_installed':
        const installCountA = Number.isInteger(a.installCount)
          ? a.installCount
          : 0;
        const installCountB = Number.isInteger(b.installCount)
          ? b.installCount
          : 0;
        result = installCountB - installCountA;
        break;
      case 'newest_to_oldest':
        result = new Date(b.createdAt) - new Date(a.createdAt);
        break;
      default: // 'highest_to_lowest_priority' handled once below
        result = 0;
    }

    // If there's a tie, sort by priority
    if (result === 0) {
      const priorityA = Number.isInteger(a.priority) ? a.priority : 0;
      const priorityB = Number.isInteger(b.priority) ? b.priority : 0;
      return priorityB - priorityA;
    }

    return result;
  };

  handleSorting = () => {
    const sortedEnvs = this.state.environments.sort((a, b) => {
      return this.compareEnvs(a, b);
    });
    this.setState({ environments: sortedEnvs });
  };

  setPackageInstallingEnv = envId => {
    this.setState({ packageInstallingEnv: envId });
    let progressId = setInterval(() => {
      this.setState(
        {
          packageProgress:
            this.state.packageProgress <= 90
              ? this.state.packageProgress + 10
              : 90
        },
        () => {
          if (this.state.packageProgress >= 90) {
            clearInterval(progressId);
          }
        }
      );
    }, 1000);
  };
  finishPackageInstalling = () => {
    this.setState({ packageProgress: 0, packageInstallingEnv: '' });
  };

  renderPopupMsg = ({ msg, type }) => {
    return (
      <Snackbar
        open={this.state.popupOpen}
        // open={true}
        autoHideDuration={4000}
        onClose={this.handlePopupClose}
        sx={{
          position: 'absolute',
          width: '100%',
          left: '0px !important',
          bottom: '0px !important'
        }}
      >
        <div
          className={`env-sidebar-msg-popup ${type} slide-in-bottom stay-longer`}
        >
          {msg}
        </div>
      </Snackbar>
    );
  };

  renderImageUploadModal = () => {
    return (
      <Dialog
        open={this.state.imageUploadBox}
        onClose={this.handleImageUploadBoxClose}
        aria-labelledby="uploadImg-dialog-title"
        aria-describedby="uploadImg-dialog-description"
        className=""
      >
        <DialogTitle
          id="uploadImg-dialog-title"
          className="env-dialog-img-title"
        >
          {'Upload Environment Image'}
        </DialogTitle>
        <DialogContent
          id="uploadImg-dialog-content"
          className="env-dialog-img-content"
        >
          <img src={this.state.img} alt="icon" className="env-dialog-img" />

          <DialogContentText id="uploadImg-dialog-description">
            Please upload a square PNG &lt; {UPLOAD_SIZE_LIMIT}KB
          </DialogContentText>
        </DialogContent>
        {this.state.img !== DEFAULT_IMG && (
          <DialogActions
            id="uploadImg-dialog-options"
            className="env-dialog-img-options"
          >
            <FormControlLabel
              control={
                <Checkbox
                  checked={this.state.imgAsIpykernelLogo}
                  onChange={this.handleUseAsIpykernelLogoChange}
                  name="imgAsIpykernelLogo"
                  color="primary"
                />
              }
              label="Override ipykernel logo"
            />
          </DialogActions>
        )}
        <DialogActions id="uploadImg-dialog-actions">
          {this.state.imgUploadError.open && (
            <Typography className="uploadImg-error-text">
              {this.state.imgUploadError.msg}
            </Typography>
          )}
          <Button
            onClick={
              this.state.img === DEFAULT_IMG
                ? this.handleImageUploadBoxClose
                : this.handleResetImg
            }
          >
            {this.state.img === DEFAULT_IMG ? 'Cancel' : 'Reset'}
          </Button>
          <Button
            component="label"
            variant="contained"
            sx={{
              backgroundColor: '#673ab7!important',
              borderColor: '#673ab7!important'
            }}
          >
            {this.state.img === DEFAULT_IMG ? 'Browse' : `Modify`}
            <input
              id="image-upload"
              hidden
              ref={this.imageInputRef}
              accept="image/*"
              type="file"
              onChange={this.handleImageUpload}
            />
          </Button>
          {this.state.img !== DEFAULT_IMG && (
            <Button
              variant="contained"
              sx={{ backgroundColor: '#673ab7!important' }}
              onClick={this.handleImageUploadBoxClose}
            >
              Save
            </Button>
          )}
        </DialogActions>
      </Dialog>
    );
  };

  renderInstalledEnvironments = () => {
    this.state.environments.sort((a, b) => {
      if (a.pinned || b.pinned) {
        return !a.pinned - !b.pinned;
      } else {
        return (b.priority || 0) - (a.priority || 0);
      }
    });
    if (this.state.environments.filter(env => env.installed).length < 1) {
      return <Loading />;
    } else {
      return this.state.environments
        .filter(env => env.installed)
        .map(env => {
          let active = env.active;
          let installing =
            this.state.installingEnvironment &&
            (this.state.installingEnvironment._id === env._id ||
              this.state.newEnvSlug === env?.slug);
          return (
            <EnvironmentTile
              qbUser={this.state.qbUser}
              key={env._id}
              expandedEnvs={this.state.expandedEnvs}
              onTogglePinned={this.onTogglePinned}
              onToggleExpand={this.onToggleExpand}
              environment={env}
              isActive={active}
              isNewEnv={env._id === this.state.newCustomEnvId ? true : false}
              isInstalling={installing}
              isInstalled={installing ? false : true}
              activateButton={
                <p
                  className="env-action"
                  style={{
                    width: '100%',
                    marginRight: 10,
                    background: installing
                      ? `linear-gradient(to right ,#673AB7 ${this.state.progress}% , #9070C8 0%)`
                      : '#673AB7',
                    cursor: installing
                      ? 'not-allowed'
                      : env.slug === 'qbraid_000000'
                        ? 'not-allowed'
                        : 'pointer'
                  }}
                  onClick={() => {
                    this.handleCheckAndActivateEnv(env);
                  }}
                >
                  {installing
                    ? 'Installing...'
                    : active
                      ? 'Remove kernel'
                      : 'Add kernel'}
                </p>
              }
              edit={() => this.handleOpenEnvEditorInstalled(env, installing)}
              flux={this.props.flux}
              packageInstallingEnv={this.state.packageInstallingEnv}
              packageProgress={this.state.packageProgress}
              cloneEnvironment={this.cloneEnvironment}
              isDarkTheme={this.state.isDarkTheme}
            />
          );
        });
    }
  };

  updateReadUserAccessData = envId => {
    // updates the selectedEnvironment state with the latest updated version of the same env from the latest list of environments
    const updatedEnv = this.state.environments.filter(env => env._id === envId);
    this.setState({
      selectedEnvironment: {
        ...this.state.selectedEnvironment,
        readAccessUsers: updatedEnv[0].readAccessUsers
      }
    });
  };

  handleAccessCodeVisibility = () => {
    this.setState(prev => ({
      accessCodeInputVisible: !prev.accessCodeInputVisible
    }));
  };

  handleAccessCodeInputChange = event => {
    this.setState({ accessCodeInput: event.target.value });
  };

  handleDiscoverEnvWithAccessCode = () => {
    if (this.state.accessCodeInput === '') return;
    this.setState({ accessCodeLoading: true });

    this.props.flux
      .getActions('EnvironmentActions')
      .searchAccessCodeAndAccept(this.state.accessCodeInput)
      .then(res => {
        if (res?.status === 200) {
          this.setState({ accessCodeInput: '', accessCodeLoading: false });
          this.handleOpenPopup('Access Code redeemed!', 'success');
          this.handleRefreshEnvironments({ clickedRefresh: false });
        }
      })
      .catch(err => {
        this.handleOpenPopup(err?.response?.body?.message, 'error');
        this.setState({ accessCodeLoading: false });
      });
  };

  handleOpenDocs = () => {
    if (this.props.app) {
      this.props.app.commands.execute('docs:qbraid-env-manager');
    }
  };

  // Shows the list of all public packages that are not installed
  renderUninstalledEnvironments = () => {
    let envs =
      this.state.filterQuery || this.state.tagFilter
        ? this.state.filteredEnvironments
        : this.state.environments;
    envs.sort((a, b) => this.compareEnvs(a, b));
    return [
      <Box m="10px">
        <Paper
          elevation={0}
          sx={theme => ({
            display: 'flex',
            flexDirection: 'row',
            flex: 1,
            borderWidth: '1px',
            borderStyle: 'solid',
            borderColor: theme.palette.grey[400],
            backgroundColor: theme.palette.background.default,
            '&:hover': {
              borderColor: `${theme.palette.action}!important`
            },
            '&:focus-within, &:focus-visible': {
              borderColor: theme.palette.primary.main,
              outline: `1px solid ${theme.palette.primary.main}`
            }
          })}
        >
          <InputBase
            sx={{
              ml: 1,
              flex: 1,
              fontSize: 18,
              fontWeight: 400
            }}
            inputProps={{
              style: {
                height: '19px',
                fontSize: '14px'
              }
            }}
            value={this.state.accessCodeInput}
            placeholder="Discover via access code..."
            onChange={this.handleAccessCodeInputChange}
            type={!this.state.accessCodeInputVisible ? 'password' : 'text'}
          />
          <IconButton size="small" onClick={this.handleAccessCodeVisibility}>
            {this.state.accessCodeInputVisible ? (
              <Visibility fontSize="inherit" />
            ) : (
              <VisibilityOff fontSize="inherit" />
            )}
          </IconButton>
          <Button
            color="secondary"
            variant="contained"
            size="small"
            sx={{
              fontSize: 14,
              textTransform: 'inherit',
              ml: 1,
              cursor: this.state.accessCodeLoading ? 'wait' : 'pointer'
            }}
            onClick={this.handleDiscoverEnvWithAccessCode}
            disabled={this.state.accessCodeLoading}
          >
            <AddCircleOutline />
          </Button>
        </Paper>
      </Box>,
      <div
        className="environments-sidebar-create-env"
        onClick={this.handleNewEnvironmentClick}
      >
        <p style={{ marginRight: 8, fontSize: 24, paddingBottom: 4 }}>+</p>
        <p>Create Environment</p>
      </div>
    ]
      .concat(
        envs
          .filter(env => !env.installed)
          .map(env => {
            return (
              <EnvironmentTile
                qbUser={this.state.qbUser}
                key={env._id}
                expandedEnvs={this.state.expandedEnvs}
                onToggleExpand={this.onToggleExpand}
                onTogglePinned={this.onTogglePinned}
                environment={env}
                isInstalling={false}
                isNewEnv={false}
                isInstalled={false}
                verifyLoading={this.state.verifyLoading}
                activateButton={
                  <p
                    className="env-action"
                    style={{
                      width: '100%',
                      marginRight: 10,
                      backgroundColor:
                        this.state.installingEnvironment || !env.isAvailable
                          ? '#a696c3'
                          : '#673ab7',
                      cursor:
                        this.state.installingEnvironment || !env.isAvailable
                          ? 'not-allowed'
                          : 'pointer'
                    }}
                    onClick={() => {
                      if (env.isAvailable) {
                        this.handleStartInstallEnvironment(env);
                      }
                    }}
                  >
                    {env.isAvailable ? 'Install' : 'Unavailable'}
                  </p>
                }
                edit={() => this.openEnvironmentEditor(env)}
                flux={this.props.flux}
                packageInstallingEnv={this.state.packageInstallingEnv}
                packageProgress={this.state.packageProgress}
                cloneEnvironment={this.cloneEnvironment}
                isDarkTheme={this.state.isDarkTheme}
              />
            );
          })
      )
      .concat([
        envs.length <= 0 && (
          <div style={{ padding: '1em' }}>
            <p
              style={{
                fontSize: 18,
                color: 'var(--jp-ui-font-color2)',
                textAlign: 'center'
              }}
            >
              No pre-configured environments found. Create a custom environment
              to get started.
            </p>
          </div>
        )
      ]);
  };

  // renderUpgradeDialogue returns a MUI dialogue box that renders on top of all active UI
  // It only shows up when showNoPermsDialog set to true
  renderUpgradeDialogue = () => {
    return (
      <Dialog
        open={this.state.showNoPermsDialog}
        onClose={this.closeNoPermsDialog}
        aria-labelledby="noPerms-dialog-title"
        aria-describedby="noPerms-dialog-description"
        className=""
      >
        <DialogTitle id="noPerms-dialog-title">Upgrade to continue</DialogTitle>
        <DialogContent id="noPerms-dialog-content">
          <DialogContentText id="noPerms-dialog-description">
            Upgrade your account to unlock premium environment manager features.
          </DialogContentText>
        </DialogContent>
        <DialogActions id="noPerms-dialog-actions">
          <Button
            onClick={this.closeNoPermsDialog}
            variant="slide"
            type="decline"
            sx={{
              minWidth: '120px'
            }}
          >
            Maybe later
          </Button>
          <Button
            variant="slide"
            onClick={() => {
              window.open(`${ACCOUNT_URL}/billing`, '_blank');
            }}
            sx={{
              minWidth: '120px'
            }}
          >
            Upgrade
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  render() {
    return (
      <ThemeProvider theme={this.state.currentTheme}>
        <div className="environments-sidebar">
          <div className="environments-sidebar-header">
            <span>
              {this.state.editingNewEnvForm ? (
                <div
                  className="environments-sidebar-back-btn"
                  style={
                    !this.state.browsing
                      ? {
                          opacity: 0,
                          cursor: 'default'
                        }
                      : null
                  }
                  onClick={this.closeNewEnvironmentForm}
                >
                  <span className="environments-sidebar-left-arrow">‹ </span>
                  Create Environment
                </div>
              ) : this.state.browsing ? (
                <div
                  className="environments-sidebar-back-btn"
                  style={
                    !this.state.browsing
                      ? {
                          opacity: 0,
                          cursor: 'default'
                        }
                      : null
                  }
                  onClick={this.closeEnvironmentBrowser}
                >
                  <span className="environments-sidebar-left-arrow">‹ </span>
                  Browse Environments
                </div>
              ) : (
                <Box
                  display="inline-flex"
                  alignItems="center"
                  gap={0.5}
                  sx={{
                    lineHeight: '20px'
                  }}
                >
                  Environments
                  <div
                    style={{
                      transition: 'transform 1s',
                      transform: `rotateZ(${`${
                        this.state.togglesCount * 180
                      }deg`})`
                    }}
                    onClick={() =>
                      this.handleRefreshEnvironments({ clickedRefresh: true })
                    }
                    className="div-refresh-btn"
                  >
                    <RefreshIcon />
                  </div>
                  <Tooltip title="Read Environment Manager docs" arrow>
                    <IconButton
                      size="small"
                      color="primary"
                      sx={{ ml: 0.5 }}
                      onClick={this.handleOpenDocs}
                    >
                      <ReceiptLongTwoTone color="inherit" fontSize="inherit" />
                    </IconButton>
                  </Tooltip>
                </Box>
              )}
            </span>
            <span
              className="environments-sidebar-add-btn"
              style={
                this.state.browsing
                  ? {
                      opacity: 0,
                      cursor: 'default'
                    }
                  : this.state.noUser
                    ? {
                        color: 'darkgray !important',
                        cursor: 'not-allowed'
                      }
                    : null
              }
              onClick={
                this.state.browsing || this.state.noUser
                  ? null
                  : () => this.handleAddButton()
              }
            >
              {this.state.qbUser.isMount ? '+ Add' : '+ Create'}
            </span>
          </div>

          <div className="environments-sidebar-spacer"></div>

          {this.state.isClickedRefresh ? (
            <Loading />
          ) : this.state.noUser ? (
            <UserNotFound />
          ) : (
            <div
              className="environments-sidebar-list-pane"
              style={
                this.state.browsing
                  ? { overflow: 'hidden', right: '100%' }
                  : null
              }
            >
              <div className="environments-sidebar-environment-list">
                {this.renderInstalledEnvironments()}
              </div>
            </div>
          )}
          <div
            className="environments-sidebar-search-pane"
            style={{
              width:
                this.state.browsing && !this.state.editingNewEnvForm
                  ? '100%'
                  : '0%'
            }}
          >
            <span className="envoronments-sidebar-search-wrapper">
              <Grid container>
                <Grid item xs={12} padding={1}>
                  <TextField
                    placeholder="Search Environments"
                    id="filled-search"
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '&.Mui-focused fieldset': {
                          borderColor: '#d30982'
                        },
                        paddingLeft: '10px',
                        paddingRight: '10px'
                      }
                    }}
                    inputProps={{
                      style: {
                        height: '19px',
                        fontSize: '14px'
                      }
                    }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <IconButton aria-label="search icon" edge="start">
                            <SearchIcon />
                          </IconButton>
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          {this.state.filterQuery.length > 1 && (
                            <Tooltip title="Clear Search" arrow={true}>
                              <IconButton
                                aria-label="clear icon"
                                edge="end"
                                onClick={() =>
                                  this.setState({
                                    filterQuery: '',
                                    filteredEnvironments: [],
                                    tagFilter: false,
                                    tags: []
                                  })
                                }
                              >
                                <ClearIcon sx={{ fontSize: '1rem' }} />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title={'Filters'} arrow={true}>
                            <IconButton
                              aria-label="filter icon"
                              edge="end"
                              onClick={() =>
                                this.setState(prev => ({
                                  showFilter: !prev.showFilter
                                }))
                              }
                            >
                              <FilterList />
                            </IconButton>
                          </Tooltip>
                        </InputAdornment>
                      )
                    }}
                    variant="outlined"
                    fullWidth
                    onChange={this.handleChangeFilterQuery}
                    value={this.state.filterQuery}
                  />
                </Grid>
                {this.state.showFilter && (
                  <Grid item xs={12} padding={1}>
                    <Grid
                      item
                      xs={12}
                      sx={{
                        backgroundColor: 'var(--jp-layout-color1)',
                        color: 'var(--jp-ui-font-color1)'
                      }}
                      paddingBottom={0}
                    >
                      <form onSubmit={this.handleAddChips}>
                        <TextField
                          fullWidth
                          size="small"
                          label="Tagged with"
                          variant="outlined"
                          placeholder="Filter environments by tag"
                          InputProps={{ sx: { textTransform: 'lowercase' } }}
                          sx={{
                            fontSize: '12px !important',
                            '& .MuiOutlinedInput-root': {
                              '&.Mui-focused fieldset': {
                                borderColor: '#d30982'
                              },
                              paddingLeft: '10px',
                              paddingRight: '10px'
                            },
                            '& .MuiInputLabel-root': {
                              fontSize: '14px !important',
                              lineHeight: '1.1em !important',
                              paddingLeft: '8px !important',
                              '& .Mui-focused': {
                                lineHeight: '1.5em !important'
                              }
                            },
                            '& .MuiOutlinedInput-input': {
                              // padding: '6px 0px !important',
                              fontSize: '14px !important',
                              textTransform: 'lowercase'
                            }
                          }}
                          value={this.state.tagsInputText}
                          onChange={e => {
                            this.setState({ tagsInputText: e.target.value });
                          }}
                          onKeyDown={e => {
                            if (e.code === 'Space') {
                              this.handleAddChips(e);
                            }
                          }}
                        />
                      </form>
                    </Grid>

                    {this.state.tags.length > 0 && (
                      <Grid item xs={12} padding={1}>
                        {this.state.tags.map(data => {
                          return (
                            <Chip
                              size="small"
                              sx={{
                                p: 1,
                                m: 0.3,
                                textTransform: 'lowercase'
                              }}
                              key={data}
                              label={data}
                              onDelete={this.handleDeleteChips(data)}
                            />
                          );
                        })}
                      </Grid>
                    )}
                    <Grid item xs={12} paddingTop={1}>
                      <TextField
                        id="outlined-select-currency"
                        select
                        fullWidth
                        size="small"
                        label="Sorted by"
                        value={this.state.sortBy}
                        sx={{
                          backgroundColor: 'var(--jp-layout-color1)',
                          color: 'var(--jp-ui-font-color1)',
                          fontSize: '14px !important',
                          mt: '5px',
                          '& .MuiOutlinedInput-root': {
                            '&.Mui-focused fieldset': {
                              borderColor: '#d30982'
                            },
                            paddingLeft: '10px',
                            paddingRight: '10px'
                          },
                          '& .MuiInputLabel-root': {
                            fontSize: '12px !important',
                            lineHeight: '1.1em !important'
                          },
                          '& .MuiSelect-select': {
                            // padding: '6px 4px !important',
                            fontSize: '14px !important',
                            lineHeight: '1.5em !important'
                          }
                        }}
                        onChange={e => {
                          this.setState(
                            {
                              sortBy: e.target.value
                            },
                            () => {
                              this.handleSorting();
                            }
                          );
                        }}
                      >
                        {filtersData.map(option => (
                          <MenuItem
                            key={option.value}
                            value={option.value}
                            sx={{
                              backgroundColor: 'var(--jp-layout-color1)',
                              color: 'var(--jp-ui-font-color1)',
                              fontSize: '14px !important',
                              '&.Mui-selected': {
                                backgroundColor: 'rgba(211, 9, 130, 0.16)'
                              }
                            }}
                          >
                            {option.label}
                          </MenuItem>
                        ))}
                      </TextField>
                    </Grid>
                  </Grid>
                )}
              </Grid>
            </span>
            <div className="environments-sidebar-spacer"></div>
            <div className="environments-sidebar-environment-list">
              {this.renderUninstalledEnvironments()}
            </div>
          </div>

          {this.state.editing && (
            <div className="overlay-background">
              <EnvironmentEditor
                qbUser={this.state.qbUser}
                onToggleExpand={this.onToggleExpand}
                env={this.state.selectedEnvironment}
                installing={
                  this.state.installingEnvironment &&
                  (this.state.installingEnvironment._id ==
                    this.state.selectedEnvironment._id ||
                    this.state.newEnvSlug ==
                      this.state.selectedEnvironment.slug)
                }
                onSave={this.handleSaveEnvironment}
                onClose={this.closeEnvironmentEditor}
                flux={this.props.flux}
                setPackageInstallingEnv={this.setPackageInstallingEnv}
                finishPackageInstalling={this.finishPackageInstalling}
                updateReadUserAccessData={this.updateReadUserAccessData}
                packageInstallingEnv={this.state.packageInstallingEnv}
                packageProgress={this.state.packageProgress}
                packageLoading={this.state.packageLoading}
              />
            </div>
          )}

          {this.state.editingNewEnvForm && (
            <div
              className="environments-sidebar-search-pane"
              style={{ width: this.state.editingNewEnvForm ? '100%' : '0%' }}
            >
              <div className="environments-sidebar-environment-list">
                <div className="environment-editor">
                  <Grid container sx={{ padding: '5px 10px', gap: '1em' }}>
                    <Grid item xs={12}>
                      <Typography
                        variant="subtitle2"
                        fontSize={12}
                        fontWeight={400}
                        color="var(--jp-layout-color4)"
                        gutterBottom
                      >
                        Name *
                      </Typography>
                      <TextField
                        fullWidth
                        placeholder="My Custom Environment"
                        value={this.state.newEnvName}
                        onChange={e => {
                          this.setState(
                            {
                              ...this.state,
                              newEnvName: e.target.value
                            },
                            () => {
                              this.setState(pre => ({
                                ...pre,
                                newEnvFormHelperTexts: pre.newEnvName.length
                                  ? {
                                      ...pre.newEnvFormHelperTexts,
                                      newEnvName: ''
                                    }
                                  : pre.newEnvFormHelperTexts
                              }));
                            }
                          );
                        }}
                        name="title"
                        size="small"
                        error={
                          this.state.newEnvFormHelperTexts.newEnvName.length
                            ? true
                            : false
                        }
                        helperText={this.state.newEnvFormHelperTexts.newEnvName}
                        sx={{
                          padding: 0,
                          fontSize: '14px',
                          '& .MuiOutlinedInput-input': {
                            padding: '0 0 0 3px'
                          }
                        }}
                        InputProps={{
                          sx: {
                            padding: '6px 14px 6px 0px',
                            fontSize: '14px',
                            height: '28px',
                            textTransform: 'lowercase'
                          }
                        }}
                        inputProps={{ maxLength: 50 }} // sets the max number of character to 50 issue#116
                        autoFocus
                      />
                      <div className="text-area-warning">
                        <p className="environment-editor-section-label text-area-warning-text">
                          {this.state.newEnvName.length >= 50 &&
                            'Max length = 50'}
                        </p>
                        <p
                          className={`environment-editor-section-label text-area-warning-text ${
                            this.state.newEnvName.length >= 50 &&
                            'text-area-error-text'
                          }`}
                        >
                          {50 - this.state.newEnvName.length}
                        </p>
                      </div>
                    </Grid>
                  </Grid>

                  <div className="environment-editor-section-label">
                    Description{' '}
                    <span style={{ color: 'var(--jp-layout-color4)' }}>
                      (optional)
                    </span>
                  </div>
                  <textarea
                    className={`environment-editor-input ${
                      this.state.newEnvDescription.length >= 300 &&
                      'text-area-error-input'
                    }`}
                    placeholder="My custom environment description"
                    // type="text"
                    spellCheck="false"
                    rows={4}
                    maxLength={300}
                    value={this.state.newEnvDescription}
                    onChange={e => {
                      this.setState({
                        ...this.state,
                        newEnvDescription: e.target.value
                      });
                    }}
                  />
                  <div className="text-area-warning">
                    <p className="environment-editor-section-label text-area-warning-text">
                      {this.state.newEnvDescription.length >= 300 &&
                        'Max length = 300'}
                    </p>
                    <p
                      className={`environment-editor-section-label text-area-warning-text ${
                        this.state.newEnvDescription.length >= 300 &&
                        'text-area-error-text'
                      }`}
                    >
                      {300 - this.state.newEnvDescription.length}
                    </p>
                  </div>
                  <p className="environment-editor-section-label">
                    Tags{' '}
                    <span style={{ color: 'var(--jp-layout-color4)' }}>
                      (optional)
                    </span>
                  </p>

                  <form
                    onSubmit={this.handleAddChips}
                    style={{ display: 'grid' }}
                  >
                    <input
                      className="environment-editor-input all_lowercase"
                      placeholder="Enter tags (e.g. qiskit, braket)"
                      type="text"
                      spellCheck="false"
                      value={this.state.tagsInputText}
                      onChange={this.handleChangeTags}
                      onKeyDown={e => {
                        if (e.code === 'Space') {
                          this.handleAddChips(e);
                        }
                      }}
                    />
                  </form>

                  <Grid container sx={{ padding: '0px 8px' }}>
                    <Grid item xs={12}>
                      {this.state.tags.map((data, index) => {
                        return (
                          <Chip
                            sx={{
                              p: 1,
                              m: 0.3,
                              textTransform: 'lowercase'
                            }}
                            size="small"
                            key={index}
                            label={data}
                            // python versions are not allowded to be deleted
                            // this can be changed
                            onDelete={
                              !this.state.pythonVersions
                                .map(item => item.value)
                                .includes(data) && this.handleDeleteChips(data)
                            }
                          />
                        );
                      })}
                    </Grid>
                  </Grid>

                  {/* Image uploading render */}
                  <p className="environment-editor-section-label">
                    Upload icon{' '}
                    <span style={{ color: 'var(--jp-layout-color4)' }}>
                      (optional)
                    </span>
                  </p>
                  <Stack
                    flexDirection="row"
                    gap={1}
                    padding={1.25}
                    alignItems="center"
                  >
                    <Avatar
                      alt=""
                      src={this.state.img}
                      sx={{
                        '.MuiAvatar-img': {
                          width: '80%',
                          height: '80%'
                        }
                      }}
                    />
                    <button
                      className={`envSidebar-custom-button envSidebar-flex-btn envSidebar-btn-upload ${
                        this.state.newEnvName.length < 1
                          ? 'envSidebar-btn-disabled'
                          : ''
                      }`}
                      onClick={this.handleImageUploadBoxOpen}
                      disabled={this.state.newEnvName.length < 1}
                    >
                      Upload Icon
                      <FileUpload fontSize="16px" />
                    </button>
                    {this.renderImageUploadModal()}
                  </Stack>

                  {/* Ace Editor render */}
                  {/* 'Packages' if slug === xcpp_d6z3gv else 'Python Packages' */}
                  <p className="environment-editor-section-label">
                    Python Packages{' '}
                    <span style={{ color: 'var(--jp-layout-color4)' }}>
                      (optional)
                    </span>
                  </p>
                  <p
                    style={{
                      color: 'var(--jp-error-color1)',
                      fontSize: '0.7em',
                      marginTop: '5px',
                      marginLeft: '10px'
                    }}
                  >
                    Warning: Environment creation will fail in the case of
                    dependency conflicts or installation errors.
                  </p>

                  <div
                    ref={this.aceContainerRef}
                    className={`environment-editor-ace-wrapper ${
                      this.state.newEnvFormHelperTexts.newEnvCode.length &&
                      'environment-editor-ace-wrapper-error'
                    }`}
                  >
                    <AceEditor
                      ref={this.aceRef}
                      onChange={this.handleChangeCode}
                      placeholder="# requirements.txt"
                      mode="python"
                      theme={
                        this.state.currentTheme === lightTheme
                          ? 'github'
                          : 'monokai'
                      }
                      name="newEnvCode"
                      style={{
                        position: 'relative',
                        flex: 1,
                        paddingBottom: 60,
                        margin: 0,
                        maxHeight: 'unset',
                        minHeight: 'unset'
                      }}
                      width={'100%'}
                      maxLines={Infinity}
                      fontSize={'auto'}
                      showGutter={true}
                      wrapEnabled={true}
                      highlightActiveLine={true}
                      value={this.state.newEnvCode}
                      setOptions={{
                        showLineNumbers: true,
                        tabSize: 2,
                        showPrintMargin: false
                      }}
                    />
                  </div>
                  <p className="environment-editor-code-error">
                    {this.state.newEnvFormHelperTexts.newEnvCode}
                  </p>
                  <StyledAccordion
                    expanded={this.state.newEnvExpandAdvanced}
                    onChange={() =>
                      this.setState({
                        newEnvExpandAdvanced: !this.state.newEnvExpandAdvanced
                      })
                    }
                  >
                    <StyledAccordionSummary>
                      <Typography color="var(--jp-layout-color4)">
                        Advanced customizations
                      </Typography>
                    </StyledAccordionSummary>
                    <StyledAccordionDetails>
                      <Grid container sx={{ gap: '1em' }}>
                        <Grid item xs={12}>
                          <Typography
                            variant="subtitle2"
                            fontSize={12}
                            fontWeight={400}
                            color="var(--jp-layout-color4)"
                            gutterBottom
                          >
                            Kernel Name (optional)
                          </Typography>

                          <TextField
                            fullWidth
                            placeholder="Python 3 [MyEnv]"
                            value={this.state.newEnvKernelName}
                            onChange={e => {
                              this.setState({
                                ...this.state,
                                newEnvKernelName: e.target.value
                              });
                            }}
                            name="title"
                            size="small"
                            // error={helperText?.title ? true : false}
                            // helperText={helperText?.title}
                            data-cy="new-snippet-title"
                            sx={{
                              padding: 0,
                              fontSize: '14px',
                              '& .MuiOutlinedInput-input': {
                                padding: '0 0 0 3px'
                              }
                            }}
                            InputProps={{
                              sx: {
                                padding: '6px 14px 6px 0px',
                                fontSize: '14px',
                                height: '28px',
                                textTransform: 'lowercase'
                              }
                            }}
                            inputProps={{ maxLength: 30 }} // sets the max number of characters
                          />
                          <div className="text-area-warning">
                            <p className="environment-editor-section-label text-area-warning-text">
                              {this.state.newEnvKernelName.length >= 30 &&
                                'Max length = 30'}
                            </p>
                            <p
                              className={`environment-editor-section-label text-area-warning-text ${
                                this.state.newEnvKernelName.length >= 30 &&
                                'text-area-error-text'
                              }`}
                            >
                              {30 - this.state.newEnvKernelName.length}
                            </p>
                          </div>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography
                            variant="subtitle2"
                            fontSize={12}
                            fontWeight={400}
                            color="var(--jp-layout-color4)"
                            gutterBottom
                          >
                            Shell Prompt (PS1) (optional)
                          </Typography>

                          <TextField
                            fullWidth
                            placeholder="e.g 'myenv' ➞ (myenv) $... when active"
                            value={this.state.newEnvShellPrompt}
                            onChange={e => {
                              this.setState({
                                ...this.state,
                                newEnvShellPrompt: e.target.value
                              });
                            }}
                            name="title"
                            size="small"
                            // error={helperText?.title ? true : false}
                            // helperText={helperText?.title}
                            data-cy="new-snippet-title"
                            sx={{
                              padding: 0,
                              fontSize: '14px',
                              '& .MuiOutlinedInput-input': {
                                padding: '0 0 0 3px'
                              }
                            }}
                            InputProps={{
                              sx: {
                                padding: '6px 14px 6px 0px',
                                fontSize: '14px',
                                height: '28px',
                                textTransform: 'lowercase'
                              }
                            }}
                            inputProps={{ maxLength: 20 }} // sets the max number of characters
                          />
                          <div className="text-area-warning">
                            <p className="environment-editor-section-label text-area-warning-text">
                              {this.state.newEnvShellPrompt.length >= 20 &&
                                'Max length = 20'}
                            </p>
                            <p
                              className={`environment-editor-section-label text-area-warning-text ${
                                this.state.newEnvShellPrompt.length >= 20 &&
                                'text-area-error-text'
                              }`}
                            >
                              {20 - this.state.newEnvShellPrompt.length}
                            </p>
                          </div>
                        </Grid>
                        <Grid item xs={12}>
                          <FormControl fullWidth>
                            <Select
                              onChange={e => {
                                e.preventDefault();
                                if (
                                  this.state.pythonVersions.filter(
                                    item => item.label === e.target.value
                                  )[0].isLocked
                                ) {
                                  return;
                                }
                                this.setState(
                                  {
                                    newEnvPythonVersion: e.target.value
                                  },
                                  () => {
                                    this.handlePythonVersionChange(
                                      e.target.value
                                    );
                                  }
                                );
                              }}
                              name="Python version"
                              value={this.state.newEnvPythonVersion}
                              size="small"
                              sx={{
                                padding: 0,
                                fontSize: '14px',
                                '& .MuiSelect-select': {
                                  display: 'flex',
                                  alignItems: 'center',
                                  padding: '4.5px 3px'
                                }
                              }}
                            >
                              {this.state.pythonVersions.map(option => (
                                <MenuItem
                                  key={option.label}
                                  value={option.label}
                                  sx={{
                                    backgroundColor: 'var(--jp-layout-color1)',
                                    color: 'var(--jp-ui-font-color1)',
                                    fontSize: '14px !important',
                                    '&.Mui-selected': {
                                      backgroundColor: 'rgba(211, 9, 130, 0.16)'
                                    }
                                  }}
                                >
                                  {!option.isLocked ? (
                                    option.label
                                  ) : (
                                    <>
                                      {option.label}
                                      <Tooltip
                                        title="Versioned Python environments coming soon!"
                                        arrow
                                      >
                                        <HttpsIcon
                                          sx={{
                                            fontSize: '14px',
                                            marginLeft: '0.5rem'
                                          }}
                                        />
                                      </Tooltip>
                                    </>
                                  )}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        </Grid>
                      </Grid>
                    </StyledAccordionDetails>
                  </StyledAccordion>
                  <div className="envSidebar-flex-container">
                    <button
                      className="envSidebar-custom-button envSidebar-flex-btn envSidebar-btn-discard"
                      onClick={this.closeNewEnvironmentForm}
                    >
                      <ClearIcon fontSize="16px" />
                      Cancel
                    </button>
                    <button
                      className={`envSidebar-custom-button envSidebar-flex-btn envSidebar-btn-save ${
                        this.state.makeNewEnv ? 'environment-editor-active' : ''
                      }`}
                      onClick={this.handleCreateEnvironmentClick}
                      disabled={this.state.installingEnvironment}
                    >
                      <DataSaverOnIcon fontSize="16px" />
                      {this.state.makeNewEnv ? 'Creating...' : 'Create'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
          {this.renderIntelTermsAndConditionModal()}
          {this.renderUpgradeDialogue()}
          {this.renderPopupMsg(this.state.popupMsg)}
        </div>
      </ThemeProvider>
    );
  }
}
