import React, { Component, Fragment } from 'react';
import contextTypes from '../contextTypes';
import '../../style/EnvironmentEditor.css';
import {
  Dialog,
  DialogActions,
  DialogTitle,
  DialogContent,
  Divider,
  IconButton,
  Grid,
  Button,
  Typography,
  Stack,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
  Tooltip,
  Paper,
  Snackbar,
  Switch,
  DialogContentText,
  Modal,
  TextField,
  InputAdornment,
  InputBase,
  LinearProgress,
  Autocomplete,
  Avatar,
  Chip,
  Box,
  FormGroup,
  FormControlLabel,
  Skeleton,
  Alert,
  Icon,
  tooltipClasses
} from '@mui/material';
import SearchIcon from '../assets/icons/SearchIcon';
import WhiteCube from '../assets/icons/WhiteCube';
import {
  AddCircleOutlined,
  AddCircleOutlineOutlined,
  BackupTwoTone,
  Check,
  Close,
  CloudDoneTwoTone,
  CloudOffTwoTone,
  CloudSyncTwoTone,
  ContentCopy,
  Edit,
  EditOff,
  InfoOutlined,
  Link,
  NotInterested,
  Refresh,
  ReportProblemOutlined,
  SaveOutlined,
  Send,
  Update,
  UpdateDisabled,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import { env } from 'process';
import { ACCOUNT_URL } from '../actions/ApiActions';
import { ConfirmIcon } from '../assets/icons/ConfirmIcon';
import { Loading } from '../assets/icons/Loading';
import _ from 'lodash';
import EnvIcon from '../assets/icons/EnvIcon';
import PublishSlider from './PublishSlider';

const PUBLISH_REQUEST_READACCESSID = '62e88a24b996354861298ab2'; // contact@qbraid.com uid
const SHARE_ENV_PERMS_NODE = 'qbraid.environments.share';
const RECENT_EMAIL_KEY = 'recent-email';
const SHARE_ENV_TIMER = 2500;
const INSTALL_ENV_PERMS_NODE = 'qbraid.environments.install';
const QSHARP_ENV_PERMS_NODE = 'qbraid.environments.qsharp';
const premiumEnvPermsNodeMap = {
  qsharp_b54crn: QSHARP_ENV_PERMS_NODE
};

function formatUTCDateTime(utcDateTimeString) {
  const date = new Date(utcDateTimeString);
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false, // Use 24-hour format
    timeZone: 'UTC'
  };
  return date.toLocaleString('en-US', options);
}

export default class EnvironmentEditor extends Component {
  static contextTypes = contextTypes;

  constructor(props, context) {
    super(props, context);
    let { env } = props;
    let envInfo = context.getStore('EnvironmentStore').getState();
    let userInfo = context.getStore('UserStore').getState();
    let user = userInfo?.user;
    let isOwner = !env ? true : !user ? false : env.owner === user._id;
    this.state = {
      // env state
      tags: env ? env.tags : [],
      packagesInImage: env ? [...env.packagesInImage] : [],
      readAccessUsers: env ? [...env.readAccessUsers] : [],
      writeAccessUsers: env ? [...env.writeAccessUsers] : [],
      quantumJobs: env ? env.quantumJobs : false,
      quantumJobsEnabled: env ? env.quantumJobsEnabled : false,
      quantumJobsAdditionSuccess: false,
      isMount: userInfo?.isMount ?? false,

      // general state
      user: user,
      isOwner: isOwner,
      canModify:
        !env || isOwner
          ? true
          : !user
            ? false
            : env.writeAccessUsers.map(u => u._id).indexOf(user._id) !== -1,
      loaded: false,
      collaboratorFilter: '',
      packageFilter: '',
      addPackageDialogOpen: false,
      searchInput: '',
      searchResults: {},
      isDropdownVisible: false,
      selectedPkg: {},
      selectedPkgVersion: '',
      selectedOperator: '==',
      availableVersions: [],
      sharePopupMsg: { msg: '', type: '' },
      editOpen: false,
      tagInput: '',
      uninstallAlert: false,
      extraUninstallAlert: false,
      optionValue: '',
      packageListLoading: false, // loading state when packageInImage list is getting searched
      packageNotInList: false,
      pkgListBusy: false, // loading state when new package gets installed or uninstalled
      popupOpen: false,
      popupMsg: { msg: '', type: '' },
      recentEmails: [], // for autocomplete dropdown options
      shareEmail: '',
      shareEmailError: '',
      shareEmailApiError: '',
      shareEmailBtnProgress: 0,
      shareEmailBtnDis: false,
      shareSuccess: false,
      sharePopupOpen: false,
      resharePopUp: false,
      upgradePopUp: false,
      qjobsStatus: { open: false, error: false, message: '' },
      isCustom: env.tags.includes('custom') ?? false,
      isShareNode:
        user?.permissionsNodes?.includes(SHARE_ENV_PERMS_NODE) ?? false,
      textCopied: false,
      isInstalled: envInfo?.environmentCache[env?._id]?.installed
        ? true
        : false,
      showCopyIcon: false,
      cancelling: false,
      cancelRequest: false,
      inputBoxVisible: false,
      saveSuccess: false,
      saveLoading: false,
      deleting: false,
      deleteAlert: false,
      loadingPackages: true,
      lockedEnv: true,
      accessKeyVisibility: false,
      accessKey: this.props.env?.accessKey || '',
      accessKeyLoading: false,
      copyCooldown: false,
      resharePopUpContent: {
        content: '',
        title: '',
        body: ''
      },
      publishLoading: false,
      actionAlert: false,
      actionAlertContext: {
        content: '',
        title: '',
        body: '',
        confirmButtonText: '',
        cancelButtonText: ''
      }
    };
  }

  componentDidMount() {
    setTimeout(this.load, 1);
    if (this.props.env) {
      setTimeout(() => {
        if (this._nameInput) {
          this._nameInput.value = this.props.env.displayName || '';
        }
        if (this._descriptionInput) {
          this._descriptionInput.value = this.props.env.description || '';
        }
      }, 1);
    }
    // gets the recent emails used for sharing
    const recentEmailListFromLocalStorage = JSON.parse(
      localStorage.getItem(RECENT_EMAIL_KEY)
    );
    if (recentEmailListFromLocalStorage) {
      this.setState({ recentEmails: recentEmailListFromLocalStorage });
      return;
    }
    this.setState({ recentEmails: [] });
  }

  static getDerivedStateFromProps(props, state) {
    if (state.loadingPackages) {
      if (props.env.packagesInImage.length !== state.packagesInImage.length) {
        return {
          ...state,
          loadingPackages: false,
          packagesInImage: props.env.packagesInImage
        };
      }
    }

    if (
      !_.isEqual(props.env.readAccessUsers.sort(), state.readAccessUsers.sort())
    ) {
      return {
        ...state,
        readAccessUsers: props.env.readAccessUsers
      };
    }

    if (props.env.installed) {
      const premiumEnvPermsNode = premiumEnvPermsNodeMap[props.env.slug];
      if (premiumEnvPermsNode) {
        if (
          !props.qbUser.user ||
          !props.qbUser.user.permissionsNodes ||
          props.qbUser.user.permissionsNodes.indexOf(premiumEnvPermsNode) === -1
        ) {
          return { ...state, lockedEnv: true };
        }
      }
      return { ...state, lockedEnv: false };
    } else {
      if (
        !props.qbUser.user ||
        !props.qbUser.user.permissionsNodes ||
        props.qbUser?.user.permissionsNodes?.indexOf(INSTALL_ENV_PERMS_NODE) ===
          -1
      ) {
        let isFree = false;
        props.env.tags.forEach(tag => {
          if (tag === 'free') {
            isFree = true;
          }
        });
        if (isFree) {
          return { ...state, lockedEnv: false };
        } else {
          return { ...state, lockedEnv: true };
        }
      } else {
        return { ...state, lockedEnv: false };
      }
    }
  }

  load = () => this.setState({ loaded: true });

  // api call, status code , error handling for sharing environment
  shareEnvironment = reShare => {
    this.setState({ shareEmailBtnDis: true });
    let shareData = {
      environmentId: this.props.env._id,
      collabEmail: this.state.shareEmail,
      overwrite: reShare || false
    };
    this.context
      .getActions('EnvironmentActions')
      .shareEnvironment(shareData)
      .then(response => {
        if (response.status === 200) {
          this.setState({
            shareSuccess: true,
            sharePopupOpen: true,
            sharePopupMsg: {
              msg: `Environment Shared Successfully`,
              type: 'success'
            }
          });
          setTimeout(() => {
            this.setState({
              shareSuccess: false,
              shareEmail: '',
              shareEmailBtnDis: false
            });
          }, SHARE_ENV_TIMER);
        }
        if (response.status === 202) {
          this.setState({
            shareSuccess: true,
            sharePopupOpen: true,
            sharePopupMsg: {
              msg: 'Environment Sharing Started',
              type: 'success'
            }
          });
          setTimeout(() => {
            this.setState({
              shareEmail: '',
              shareEmailBtnDis: false,
              shareSuccess: false
            });
          }, SHARE_ENV_TIMER);
        }
        if (response.status === 304 && !reShare) {
          this.setState({
            resharePopUp: true,
            resharePopUpContent: {
              content: 'reShareEnv',
              title: 'Update Shared Environment?',
              body: `You have already shared this environment with ${
                this.state.shareEmail
                  ? `${this.state.shareEmail}, or another user`
                  : 'one or more users'
              }. Would you like to update the existing version? Doing so will overwrite the globally shared environment, but will not affect any local copies that users have already installed.`
            }
          });
        }
      })
      .then(() => {
        this.props.flux
          .getActions('EnvironmentActions')
          .updateAll()
          .then(() => {
            this.props.updateReadUserAccessData(this.props.env._id);
            this.props.flux
              .getActions('EnvironmentActions')
              .registerInstalled();
          });
      })
      .catch(error => {
        if (error?.status) {
          if (error.status === 404) {
            this.setState({
              shareEmailApiError: 'Invalid User Mail',
              shareEmailBtnDis: false,
              shareSuccess: false,
              sharePopupOpen: true,
              sharePopupMsg: { msg: 'Invalid User Mail', type: 'error' }
            });
          } else if (error.status === 304 && !reShare) {
            this.setState({
              resharePopUp: true
            });
          } else {
            this.setState({
              shareEmailApiError: 'Environment sharing failed',
              shareEmailBtnDis: false,
              shareSuccess: false,
              sharePopupOpen: true,
              sharePopupMsg: {
                msg: 'Environment sharing failed',
                type: 'error'
              }
            });
          }
        } else {
          this.setState({
            shareEmailApiError: error,
            shareEmailBtnDis: false,
            shareSuccess: false,
            sharePopupOpen: true,
            sharePopupMsg: { msg: error, type: 'error' }
          });
        }
      });
  };

  requestPublishEnvironment = () => {
    if (!this.state.isCustom) {
      this.setState({
        sharePopupOpen: true,
        sharePopupMsg: {
          msg: 'Only custom environment can be published',
          type: 'error'
        }
      });
      return;
    }
    if (
      this.state.uninstalling ||
      this.state.cancelling ||
      this.state.deleting ||
      this.props.installing ||
      this.props.packageInstallingEnv === this.props.env._id
    ) {
      this.setState({
        sharePopupOpen: true,
        sharePopupMsg: {
          msg: 'Blocked during state transition',
          type: 'error'
        }
      });
      return;
    }
    this.setState({ publishLoading: true });
    let publishData = {
      environmentId: this.props.env._id,
      collabEmail: 'contact@qbraid.com',
      overwrite: true
    };
    this.context
      .getActions('EnvironmentActions')
      .shareEnvironment(publishData)
      .then(response => {
        if (response.status === 200 || response.status === 202) {
          this.setState({
            sharePopupOpen: true,
            sharePopupMsg: {
              msg: 'Submitting your request! Please wait...',
              type: 'success'
            }
          });
          this.context
            .getActions('EnvironmentActions')
            .updatePublishStatus(this.props.env.slug, 'requested')
            .then(resp => {
              if (resp?.status === 200) {
                this.setState({
                  sharePopupOpen: true,
                  sharePopupMsg: {
                    msg: 'Successfully Requested to publish',
                    type: 'success'
                  }
                });
              }
            });
        }
      })
      .then(() => {
        this.props.flux
          .getActions('EnvironmentActions')
          .updateAll()
          .then(() => {
            this.props.updateReadUserAccessData(this.props.env._id);
            this.props.flux
              .getActions('EnvironmentActions')
              .registerInstalled()
              .then(() => {
                this.setState({ publishLoading: false });
              });
          });
      })
      .catch(error => {
        console.warn(error);
        this.setState({
          sharePopupOpen: true,
          sharePopupMsg: { msg: 'Request to publish failed', type: 'error' },
          publishLoading: false
        });
      });
  };
  denyPublishingEnvironment = () => {
    if (!this.state.isMount) {
      return;
    }

    if (this.state.user.email !== 'contact@qbraid.com') {
      this.setState({
        sharePopupOpen: true,
        sharePopupMsg: {
          msg: 'Only contact@qbraid.com can deny publishing this environment',
          type: 'error'
        }
      });
      return;
    }
    this.props.flux
      .getActions('EnvironmentActions')
      .updatePublishStatus(this.props.env.slug, 'denied')
      .then(res => {
        if (res.status === 200) {
          this.setState({
            sharePopupOpen: true,
            sharePopupMsg: {
              msg: 'Publishing request denied!',
              type: 'error'
            }
          });
        }
      })
      .then(() => {
        this.props.flux
          .getActions('EnvironmentActions')
          .updateAll()
          .then(() => {
            this.props.flux
              .getActions('EnvironmentActions')
              .registerInstalled();
          });
      })
      .catch(error => {
        console.warn(error);
        this.setState({
          sharePopupOpen: true,
          sharePopupMsg: { msg: 'Publish failed', type: 'error' },
          publishLoading: false
        });
      });
  };

  publishEnvironment = () => {
    if (!this.state.isMount) {
      return;
    }
    if (this.state.user.email !== 'contact@qbraid.com') {
      this.setState({
        sharePopupOpen: true,
        sharePopupMsg: {
          msg: 'Only contact@qbraid.com can publish environment',
          type: 'error'
        }
      });
      return;
    }
    this.props.flux
      .getActions('EnvironmentActions')
      .publishEnvironment(this.props.env.slug)
      .then(res => {
        if (res.status === 200) {
          this.setState({
            sharePopupOpen: true,
            sharePopupMsg: {
              msg: 'Environment published successfully',
              type: 'success'
            }
          });
        }
      })
      .then(() => {
        this.props.flux
          .getActions('EnvironmentActions')
          .updateAll()
          .then(() => {
            this.props.flux
              .getActions('EnvironmentActions')
              .registerInstalled();
          });
      })
      .catch(error => {
        console.warn(error);
        this.setState({
          sharePopupOpen: true,
          sharePopupMsg: { msg: 'Publish failed', type: 'error' },
          publishLoading: false
        });
      });
  };

  toggleWriteAccess = user => {
    let { readAccessUsers, writeAccessUsers } = this.state;
    if (user.write) {
      // remove write access
      delete user.write;
      readAccessUsers = readAccessUsers.filter(u => u._id !== user._id); // remove beforehand to prevent duplication
      readAccessUsers.push(user);
      writeAccessUsers = writeAccessUsers.filter(u => u._id !== user._id);
      return this.setState({ readAccessUsers, writeAccessUsers });
    }
    // add write access
    writeAccessUsers = writeAccessUsers.filter(u => u._id !== user._id); // remove beforehand to prevent duplication
    writeAccessUsers.push(user);
    readAccessUsers = readAccessUsers.filter(u => u._id !== user._id);
    return this.setState({ readAccessUsers, writeAccessUsers });
  };

  openAddPackageDialog = () => {
    //alert('Ad-hoc package addition is temporarily disabled');
    this.setState({ addPackageDialogOpen: true });
  };

  closeAddPackageDialog = () => {
    this.setState({
      addPackageDialogOpen: false,
      searchInput: '',
      isDropdownVisible: false,
      packageNotInList: false,
      packageFilter: ''
    });
    if (!this.state.pkgListBusy) {
      this.setState({
        selectedPkg: {},
        selectedPkgVersion: ''
      });
    }
  };

  handleSelectPackage = pkg => {
    this.setState({ selectedPkg: pkg });
  };

  registerInstallingNull = async (pkgToAdd, installMessage) => {
    const res = await this.context
      .getActions('EnvironmentActions')
      .registerInstallingNull();
    if (res) {
      this.props.finishPackageInstalling();
      // this.props.finishPackageInstalling();
      let pattern = /(==|~=|<|<=|>|>=)/;
      let packageName = pkgToAdd.split(pattern)[0];
      const isReady = 'is now ready-to-use in your environment.';
      let alertMessage =
        installMessage && installMessage.length > 0
          ? `${installMessage}\n\n${packageName} ${isReady}`
          : `Package install complete!\n\n${pkgToAdd} ${isReady}`;
      this.setState({ pkgListBusy: false });
      alert(alertMessage);
      this.setState({ packagesInImage: this.props.env.packagesInImage });
    }
  };

  updatePackageList = async (pkgToAdd, errMsg, installMessage) => {
    try {
      const data = await this.context
        .getActions('EnvironmentActions')
        .updatePackagesList(this.props.env._id);
      if (data) {
        this.registerInstallingNull(pkgToAdd, installMessage);
      }
    } catch (err) {
      this.props.finishPackageInstalling();
      console.log(err);
      this.setState({ pkgListBusy: false });
      alert(errMsg);
    }
  };

  pollStatusLocal = async (pkgToAdd, errMsg, installMessage) => {
    try {
      const data = await this.context
        .getActions('EnvironmentActions')
        .pollStatusLocal();
      if (data) {
        installMessage = data.message ? data.message : '';
        installMessage = installMessage.includes('ERROR')
          ? installMessage.replace('Successfully', '\n\nSuccessfully')
          : installMessage;
        if (data.success === true) {
          this.updatePackageList(pkgToAdd, errMsg, installMessage);
        } else {
          this.props.finishPackageInstalling();
          alert(errMsg);
        }
      }
    } catch (err) {
      console.log(err);
      this.props.finishPackageInstalling();
      this.setState({ pkgListBusy: false });
      alert(errMsg);
    }
  };

  registerInstalling = async (pkgToAdd, errMsg, installMessage) => {
    const data = await this.context
      .getActions('EnvironmentActions')
      .registerInstalling(this.props.env._id);
    return new Promise((resolve, reject) => {
      if (data) {
        setTimeout(() => {
          this.pollStatusLocal(pkgToAdd, errMsg, installMessage);
          resolve(true);
        }, 30000);
      } else {
        reject(false);
      }
    });
  };

  // function to add Package to the existing environment
  addPackage = async pkgToAdd => {
    if (this.state.packagesInImage.indexOf(pkgToAdd) !== -1) {
      return false;
    }
    this.setState({
      loadingPackages: false,
      packagesInImage: this.state.packagesInImage.concat([pkgToAdd])
    });
    let installData = {
      slug: this.props.env.slug,
      packages: [pkgToAdd],
      upgradePip: false,
      systemSitePackages: this.props.env.systemSitePackages ?? true
    };
    let installMessage;
    let errMsg = `Error installing package ${pkgToAdd}.`;
    try {
      const data = await this.context
        .getActions('EnvironmentActions')
        .installPackagesPyvenv(installData);
      if (data && (data.status === 200 || data.status === 202)) {
        this.props.setPackageInstallingEnv(this.props.env._id);
        const response = await this.registerInstalling(
          pkgToAdd,
          errMsg,
          installMessage
        );
        if (response) {
          this.updateCustomPackageListInMongo();
        }
        if (pkgToAdd.startsWith('amazon-braket-sdk')) {
          this.setState({ quantumJobs: true });
        }
      }
    } catch (err) {
      this.props.finishPackageInstalling();
      console.log(err);
      alert(errMsg);
    }
  };

  removePackage = pkgToRemove => {
    this.setState({ loadingPackages: false });

    const pattern = /(==|~=|<|<=|>|>=)/;
    const name = pkgToRemove.split(pattern)[0];
    const slug = this.props.env.slug;
    if (!name || !slug) {
      alert(
        'Failed to uninstall package: environment slug or package name not found'
      );
      return;
    }
    const uninstallData = {
      slug: slug,
      package: name
    };

    return new Promise(resolve => {
      this.props.flux
        .getActions('EnvironmentActions')
        .uninstallPackagePyvenv(uninstallData)
        .then(status => {
          // only 202 is considered, other status codes need to be handled according to backend update
          if (status === 202) {
            if (name === 'amazon-braket-sdk' || name === 'botocore') {
              this.setState({ quantumJobs: false, quantumJobsEnabled: false });
            }

            this.setState({
              packagesInImage: this.state.packagesInImage.filter(
                pkg => pkg !== pkgToRemove
              )
            });
            resolve(true);
          } else {
            reject(status);
          }
        })
        .catch(err => {
          reject(err);
        });
    });
  };

  handleRemovePkg = async pkg => {
    const name = pkg.split('==')[0];
    const res = await this.removePackage(pkg);
    if (res) {
      this.setState({
        popupOpen: true,
        popupMsg: { msg: `Uninstalling ${name}...`, type: 'success' }
      });
      this.updateCustomPackageListInMongo();
    } else {
      this.setState({
        popupOpen: true,
        popupMsg: { msg: `Failed to uninstall ${name}`, type: 'error' }
      });
    }
  };

  updateCustomPackageListInMongo = async () => {
    if (this.state.isCustom) {
      const allEnvs = await this.context
        .getActions('EnvironmentActions')
        .fetchAllEnv();
      const currentEnvFromMongo = allEnvs.filter(e => e.slug === env.slug)[0];

      // Boolean: gets whether the currentPackages are same with package on Mongo DB
      const isPackageSame = this.comparePackageList(currentEnvFromMongo);
      if (!isPackageSame) {
        await this.context
          .getActions('EnvironmentActions')
          .updateCustomPackageListInMongoDB({
            slug: this?.props?.env?.slug,
            packageList: this.state.packagesInImage
          });
      }
    }
  };

  comparePackageList = envFromMongo =>
    _.isEqual(envFromMongo?.packagesInImage, this.state.packagesInImage);

  handleChangePackageFilter = (event, type) => {
    // gets triggered when package name are searched in package list pane
    this.setState(
      { packageFilter: event.target.value.trim().toLowerCase() },
      () => {
        if (this.state.packageFilter !== '' && this.props.env.installed) {
          const filterPackLength = this.state.packagesInImage.filter(
            pkg =>
              pkg
                .split('=')[0]
                .toLowerCase()
                .trim()
                .indexOf(this.state.packageFilter.replaceAll('-', '')) !== -1
          ).length; // gets the number of PACKAGES FOUND from the existing list of packages in the current environment

          if (filterPackLength === 0 && !this.props.env.isPreInstalled) {
            // package not found in env package list
            this.setState({
              addPackageDialogOpen: true,
              packageListLoading: true,
              searchInput: this.state.packageFilter
            });
            if (type) {
              this.setState({
                packageNotInList: false
              });
            } else {
              this.setState({
                packageNotInList: true
              });
            }
            if (!this.state.packageNotInList) {
              setTimeout(() => {
                this.setState({
                  packageNotInList: false,
                  packageListLoading: false,
                  packageFilter: ''
                });
              }, 3000);
            }
          }
        }
      }
    );
  };

  handleChangeCollaboratorFilter = event =>
    this.setState({
      collaboratorFilter: event.target.value.trim().toLowerCase()
    });

  handleUninstall = () => {
    if (this.state.cancelling || this.state.uninstalling) {
      return;
    }
    this.state.cancelRequest
      ? this.setState({
          uninstallAlert: false,
          extraUninstallAlert: false,
          cancelling: true
        })
      : this.setState({
          uninstallAlert: false,
          extraUninstallAlert: false,
          uninstalling: true
        });
    if (this.state.isCustom && this.state.isOwner) {
      this.context
        .getActions('EnvironmentActions')
        .deleteEnvironment(this.props.env.slug);
    }
    this.context
      .getActions('EnvironmentActions')
      .uninstall(this.props.env.slug)
      .then(() => {
        this.setState(
          { uninstalling: false, cancelling: false, cancelRequest: false },
          () => {
            this.props.onClose();
            this.props.onToggleExpand(this.props.env._id);
          }
        );
      })
      .catch(err => {
        console.log(err);
        alert('This environment cannot be uninstalled.');
      });
  };

  handleDelete = () => {
    if (this.state.deleting) return null;
    try {
      this.setState({ deleting: true, deleteAlert: false });
      this.context
        .getActions('EnvironmentActions')
        .deleteEnvironment(this.props.env.slug)
        .then(() => {
          this.setState({ deleting: false });
          this.props.onClose();
          this.context
            .getActions('EnvironmentActions')
            .updateAll()
            .then(() => {
              this.context.getActions('EnvironmentActions').registerInstalled();
            });
        })
        .catch(err => {
          console.log('Error deleting environment: ', err);
          alert('Environment cannot be deleted at this time.');
        });
    } catch (err) {
      this.setState({ deleting: false, deleteAlert: false });
    }
  };

  handleSubmit = () => {
    this.setState({ saveLoading: true });
    let displayName = this._nameInput.value.trim();
    if (!displayName) {
      return this._nameInput.focus();
    }
    let description = this._descriptionInput.value.trim();

    let { packagesInImage, readAccessUsers, writeAccessUsers, tags } =
      this.state;
    try {
      if (this.props.env) {
        // edit existing
        this.context
          .getActions('EnvironmentActions')
          .editOne(this.props.env._id, {
            displayName,
            description,
            tags,
            packagesInImage,
            readAccessUsers,
            writeAccessUsers
          })
          .then(() => {
            this.context
              .getActions('EnvironmentActions')
              .updateAll()
              .then(() => {
                this.context
                  .getActions('EnvironmentActions')
                  .registerInstalled()
                  .then(() => {
                    this.setState({
                      saveSuccess: true,
                      editOpen: false,
                      saveLoading: false
                    });
                    setTimeout(() => {
                      this.setState({ saveSuccess: false });
                    }, 2500);
                  })
                  .catch(err => {
                    console.log(err);
                    this.props.onClose();
                  });
              });
          });
      }
    } catch (err) {
      console.log('Unable to save env || Error: ', err);
    }
  };

  // fetch the values from PyPi
  fetchFromPyPi = async value => {
    await fetch(`https://pypi.org/pypi/${value}/json`)
      .then(res => {
        if (res.ok) {
          return res.json();
        }
        throw new Error('Package doesnt exist');
      })
      .then(data => {
        this.setState({
          searchResults: data,
          availableVersions: Object.keys(data.releases)
            .map(a => a.replace(/\d+/g, n => +n + 100000))
            .sort()
            .reverse()
            .map(a => a.replace(/\d+/g, n => +n - 100000))
        });
      })
      .then(_data => {
        const filteredPkg = this.state.packagesInImage.filter(pkg =>
          pkg.includes(this.state.searchResults?.info?.name)
        )[0];
        if (_.isEmpty(filteredPkg)) {
          this.setState({
            selectedPkgVersion: 'any'
          });
        } else {
          this.setState({
            selectedPkgVersion: filteredPkg.split('==')[1]
          });
        }
      })
      .catch(error => {
        this.setState({
          searchResults: {},
          selectedPkgVersion: '',
          availableVersions: []
        });
        return console.log(error);
      });
  };

  // handles onKeyPress from pypi package search
  handleEnterKeypress = e => {
    if (e.key === 'Enter') {
      this.setState({
        searchInput: e.target.value,
        isDropdownVisible: true,
        packageNotInList: false
      });
      this.fetchFromPyPi(this.state.searchInput);
    }
  };

  // handles search button click
  handleSearchSubmit = () => {
    this.setState({ isDropdownVisible: true, packageNotInList: false });
    this.fetchFromPyPi(this.state.searchInput);
  };

  //handle onChanges from searchbar
  handleInputChanges = e => {
    this.setState({ searchInput: e.target.value });
    this.handleChangePackageFilter(e, true);
    if (this.state.searchInput.length <= 3) {
      this.setState({ isDropdownVisible: false });
    }
  };

  handleAddPackageToList = async value => {
    if (!_.isEmpty(this.state.selectedPkg)) {
      this.setState({ pkgListBusy: true });
      this.closeAddPackageDialog();
      let newValue = value;
      const pattern = /(==|~=|<|<=|>|>=)/;
      const extractNumbersRegex = /[\d|,|.|e|E|\+]+/g;

      // makes an array of objects {name: 'name_of_the_pkg',version: 'version_of_the_pkg', pkg: 'original_string'} of all the packages present in current env
      const packageArray = this.state.packagesInImage.map(pkg => {
        return {
          name: pkg.split(pattern)[0].toLowerCase().trim(),
          version: pkg
            ?.split(pattern)[2]
            ?.toLowerCase()
            ?.trim()
            ?.match(extractNumbersRegex)[0], // extra regex step taken since some pkg versions has words after version which when comparing could pose a problem
          pkg: pkg
        };
      });

      // makes array of all the release version available of a selected package user want to install
      const pkgReleases = Object.keys(this.state.selectedPkg.releases);

      // replaces the newValue's package version with the package selected
      // the version and the operator sign gets replaced
      // input: value='abcd<=1.2.4', output: value='abcd==1.2.3'
      if (this.state.selectedOperator !== '==') {
        let versionTobeinstalled = this.state.selectedPkgVersion;
        if (this.state.selectedOperator === '>') {
          versionTobeinstalled = pkgReleases
            .filter(release => release > this.state.selectedPkgVersion)
            .slice(-1); // picks the nearest version available
        } else if (this.state.selectedOperator === '>=') {
          versionTobeinstalled = pkgReleases
            .filter(release => release >= this.state.selectedPkgVersion)
            .slice(-1); // picks the nearest version available
        } else if (this.state.selectedOperator === '<') {
          versionTobeinstalled = pkgReleases
            .filter(release => release < this.state.selectedPkgVersion)
            .slice(-1); // picks the nearest version available
        } else if (this.state.selectedOperator === '<=') {
          versionTobeinstalled = pkgReleases
            .filter(release => release <= this.state.selectedPkgVersion)
            .slice(-1); // picks the nearest version available
        }
        if (versionTobeinstalled) {
          newValue = newValue
            .replace(this.state.selectedPkgVersion, versionTobeinstalled)
            .split(this.state.selectedOperator)
            .join('==');
        } else {
          this.setState({
            popupOpen: true,
            popupMsg: {
              msg: `Package version is not available`,
              type: 'error'
            }
          });
        }
      } else if (
        this.state.selectedOperator === '==' &&
        this.state.selectedPkgVersion === 'any'
      ) {
        newValue = this.state.selectedPkg.info.name;
      }

      // finds if the package selected already exist in the env
      const isExisting = packageArray.find(
        pkg => pkg.name === this.state.selectedPkg.info.name
      );

      // if selected package version is "Any" from the dropdown, then selectedVersion should be blank
      // version also contain values like '1.0.2.post0' which cannot be compared. Matching with regex gives only the number
      const selectedVersion =
        this.state.selectedPkgVersion === 'any'
          ? ''
          : this.state.selectedPkgVersion.match(extractNumbersRegex)[0];

      if (
        isExisting &&
        selectedVersion !== '' &&
        selectedVersion > isExisting.version
      ) {
        // if package exist but the selected version is greater than the installed version
        // action: popup a message, uninstall older pkg and install the new one
        this.setState({
          popupOpen: true,
          popupMsg: {
            msg: `Upgrading to version ${this.state.selectedPkg?.info?.version}`,
            type: 'success'
          }
        });
        const isUninstalled = await this.removePackage(isExisting.pkg);
        if (isUninstalled) {
          this.addPackage(newValue);
        }
      } else if (
        isExisting &&
        selectedVersion !== '' &&
        isExisting.version > selectedVersion
      ) {
        // if package exist but the selected version is less than the installed version
        // popup a message, uninstall older pkg and install the new one
        this.setState({
          popupOpen: true,
          popupMsg: { msg: `Downgrading to selected version`, type: 'success' }
        });

        const isUninstalled = await this.removePackage(isExisting.pkg);
        if (isUninstalled) {
          this.addPackage(newValue);
        }
      } else if (
        isExisting &&
        selectedVersion !== '' &&
        selectedVersion === isExisting.version
      ) {
        // if package exist but the selected version is same as the installed version
        // popup an error message and dont do anything
        this.setState({
          popupOpen: true,
          popupMsg: { msg: `Already installed`, type: 'error' },
          pkgListBusy: false
        });

        return;
      } else {
        // for new pkg, install the pkg
        this.addPackage(newValue);

        this.setState({
          popupOpen: true,
          popupMsg: { msg: `Package install started!`, type: 'success' }
        });
      }
      this.setState({
        isDropdownVisible: false,
        selectedPkg: {},
        searchInput: ''
      });
    }
  };

  handlePopupClose = () => {
    this.setState({ popupOpen: false });
  };

  handleSharePopupClose = () => {
    this.setState({ sharePopupOpen: false });
  };

  handleEditStateOpen = () => {
    this.setState({ editOpen: true });
  };

  handleEditStateClose = () => {
    this.setState({
      editOpen: false,
      inputBoxVisible: false,
      tags: this.props.env?.tags || [],
      tagsInput: ''
    });
    this._descriptionInput.value = this.props.env?.description || '';
  };

  handleAddTags = e => {
    if (e.key === 'Enter' || e.code === 'Space') {
      if (e.target.value.toLowerCase() !== 'custom') {
        this.setState({
          tags: [...new Set([...this.state.tags, e.target.value.toLowerCase()])]
        });
      }
      this.setState({
        tagInput: ''
      });
    }
  };

  handleRemoveTags = id => {
    this.setState({
      tags: this.state.tags.filter(
        (tag, index) => index !== id || tag === 'custom'
      )
    });
  };

  resetQjobsStatus = () => {
    setTimeout(() => {
      this.setState({
        qjobsStatus: {
          open: false,
          error: false,
          message: ''
        }
      });
    }, 2500);
  };

  handleQuantumJobsToggle = () => {
    if (this.state.lockedEnv) return null;
    if (this.props.env) {
      const initialJobsState = this.state.quantumJobsEnabled;
      this.setState({ pkgListBusy: true });
      this.context
        .getActions('EnvironmentActions')
        .toggleQuantumJobs({
          slug: this.props.env.slug,
          action: this.state.quantumJobsEnabled ? 'disable' : 'enable'
        })
        .then(data => {
          const { success } = data;
          const newState = {
            pkgListBusy: false,
            quantumJobsEnabled: success ? !initialJobsState : initialJobsState,
            qjobsStatus: {
              open: true,
              error: !success,
              message: success
                ? initialJobsState
                  ? 'Disabled'
                  : 'Enabled'
                : initialJobsState
                  ? 'Enabled'
                  : 'Disabled'
            }
          };

          // Set the new Quantum Jobs state
          this.setState(newState);
          this.resetQjobsStatus();
        })
        .catch(err => {
          console.log('Quantum Jobs Toggle Error: ', err);
          this.setState({
            pkgListBusy: false,
            qjobsStatus: {
              open: true,
              error: true,
              message: 'Error: failed to enable Quantum Jobs'
            }
          });

          // Reset the Quantum Jobs state
          this.resetQjobsStatus();
        });
    }
  };

  handleUninstallAlertOpen = () => {
    this.setState({ uninstallAlert: true });
  };

  handleUninstallAlertClose = () => {
    this.setState({ uninstallAlert: false, cancelRequest: false });
  };

  handleExtraUninsConfirmOpen = () => {
    this.setState({ extraUninstallAlert: true });
  };

  handleExtraUninsConfirmClose = () => {
    this.setState({ extraUninstallAlert: false, cancelRequest: false });
  };

  handleDeleteAlertOpen = () => {
    this.setState({ deleteAlert: true });
  };
  handleDeleteAlertClose = () => {
    this.setState({ deleteAlert: false });
  };

  handleCustomUninstall = () => {
    if (this.state.uninstalling || this.state.cancelling) {
      return null;
    }

    if (this.state.isCustom) {
      this.setState({ uninstallAlert: false });
      this.handleExtraUninsConfirmOpen();
    } else {
      this.handleUninstall();
    }
  };

  handleCancelReq = () => {
    this.setState({ cancelRequest: true });
    this.handleUninstallAlertOpen();
  };
  renderEditTags = () => {
    if (this.state.isOwner) {
      return this.state.editOpen ? (
        <>
          <Tooltip title="Turn editing tags off">
            <EditOff className="env-edit-icon" onClick={this.handleEditState} />
          </Tooltip>
          {this.renderAddTags()}
        </>
      ) : (
        <Tooltip title="Turn editing tags on">
          <Edit className="env-edit-icon" onClick={this.handleEditState} />
        </Tooltip>
      );
    }
  };

  renderAddTags = () => {
    const toggleInputBox = () => {
      this.setState(prevState => ({
        inputBoxVisible: !prevState.inputBoxVisible
      }));
    };

    return (
      <div
        className="env-add-tags"
        style={{ backgroundColor: this.state.inputBoxVisible && '#673ab7' }}
      >
        <IconButton
          size="small"
          onClick={toggleInputBox}
          sx={{
            padding: 0,
            fontSize: 14,
            color: this.state.inputBoxVisible && 'white'
          }}
        >
          <AddCircleOutlined fontSize="inherit" color="inherit" />
        </IconButton>
        {this.state.inputBoxVisible && (
          <input
            className="env-tags-input"
            type="text"
            value={this.state.tagInput}
            placeholder="Enter tags"
            onChange={e => this.setState({ tagInput: e.target.value })}
            onKeyDown={e => this.handleAddTags(e)}
          />
        )}
      </div>
    );
  };

  renderQuantumJobsToggle = () => {
    const hasQuantumJobs = this.state.quantumJobs;

    const handleAddQuantumJobs = async () => {
      this.addPackage('amazon-braket-sdk')
        .then(() => {
          this.setState({ quantumJobsAdditionSuccess: true });
          setTimeout(() => {
            this.setState({
              quantumJobsAdditionSuccess: false,
              quantumJobs: true,
              quantumJobsEnabled: false
            });
          }, 1750);
        })
        .catch(err => {
          console.log('Error adding quantum jobs. ', err);
          alert(
            'Unable to add quantum jobs at this time. ' +
              'Please try again later, and verify that qbraid-core ' +
              'is installed and configured correctly.'
          );
        });
    };

    return (
      <Stack
        flexDirection="row"
        alignItems="center"
        flexWrap="wrap"
        gap={1}
        px="12px"
        pb="12px"
      >
        <Typography
          fontSize={14}
          fontWeight={600}
          color={hasQuantumJobs ? 'text.primary' : 'text.disabled'}
          sx={{ userSelect: 'none' }}
        >
          Quantum Jobs
        </Typography>
        {hasQuantumJobs && (
          <FormGroup>
            <FormControlLabel
              disabled={!hasQuantumJobs}
              control={
                <Switch
                  disabled={this.state.lockedEnv}
                  checked={this.state.quantumJobsEnabled}
                  onChange={this.handleQuantumJobsToggle}
                  size="small"
                  inputProps={{ 'aria-label': 'controlled' }}
                  sx={{
                    cursor:
                      (!hasQuantumJobs || this.state.lockedEnv) && 'not-allowed'
                  }}
                />
              }
              label={
                hasQuantumJobs
                  ? this.state.qjobsStatus.message
                    ? this.state.qjobsStatus.message
                    : this.state.quantumJobsEnabled
                      ? 'Enabled'
                      : 'Disabled'
                  : ''
              }
              sx={{
                margin: 0,
                '& .MuiFormControlLabel-label': {
                  fontSize: '12px',
                  color: !this.state.qjobsStatus.error
                    ? this.state.quantumJobsEnabled
                      ? 'success.main'
                      : 'text.disabled'
                    : 'error.main'
                }
              }}
            />
          </FormGroup>
        )}
        {!hasQuantumJobs && !this.state.quantumJobsAdditionSuccess && (
          <Tooltip
            title="Quantum jobs are not supported for this environment!"
            arrow
            placement="right"
            PopperProps={{
              sx: theme => ({
                '& .MuiTooltip-tooltip': {
                  backgroundColor: theme.palette.warning.main,
                  color: theme.palette.warning.contrastText,
                  boxShadow: theme.shadows[5],
                  fontSize: '12px'
                },
                '& .MuiTooltip-arrow': {
                  color: theme.palette.warning.main
                }
              })
            }}
          >
            <ReportProblemOutlined
              color="inherit"
              sx={{ color: 'warning.main', fontSize: '16px' }}
            />
          </Tooltip>
        )}
        {!hasQuantumJobs && !this.state.quantumJobsAdditionSuccess && (
          <Tooltip
            title="Add quantum jobs"
            arrow
            placement="right"
            PopperProps={{
              sx: theme => ({
                '& .MuiTooltip-tooltip': {
                  backgroundColor: theme.palette.background.paper,
                  color: theme.palette.text.secondary,
                  boxShadow: theme.shadows[5],
                  fontSize: '12px'
                },
                '& .MuiTooltip-arrow': {
                  color: theme.palette.background.paper
                }
              })
            }}
          >
            <IconButton
              size="small"
              color="text.secondary"
              disabled={
                this.props.installing ||
                this.props.env.isPreInstalled ||
                this.state.lockedEnv
              }
              onClick={!this.props.env.isPreInstalled && handleAddQuantumJobs}
            >
              <AddCircleOutlineOutlined fontSize="inherit" />
            </IconButton>
          </Tooltip>
        )}
        {this.state.quantumJobsAdditionSuccess && (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            gap={1}
            borderRadius={1}
            px={1}
            sx={theme => ({
              userSelect: 'none'
            })}
          >
            <ConfirmIcon color="green" />
            <Typography
              fontSize={14}
              sx={theme => ({ color: theme.palette.success.main })}
            >
              Successfully added!
            </Typography>
          </Box>
        )}
      </Stack>
    );
  };

  // Edit environment, general info container
  renderInfoPane = () => {
    return (
      <div className="env-editor-pane" id="general-info-pane">
        <p className="env-editor-pane-title">General Info</p>
        <TextField
          inputRef={el => (this._nameInput = el)}
          class="env-editor-input-data-text"
          placeHolder="Name"
          fullWidth
          size="small"
          sx={{ padding: '0' }}
          spellCheck="false"
          //disabled={!this.state.isOwner}
          disabled
          InputProps={{
            endAdornment: (
              <InputAdornment
                position="end"
                sx={{
                  textDecoration: this.state.showCopyIcon
                    ? 'underline'
                    : 'none',
                  cursor: 'pointer'
                }}
                onMouseEnter={() => {
                  this.setState({ showCopyIcon: true });
                }}
                onMouseLeave={() => {
                  this.setState({ showCopyIcon: false });
                }}
              >
                {`ID: ${this.props.env.slug}`}
                {this.state.showCopyIcon && (
                  <Tooltip
                    title={
                      this.state.textCopied
                        ? 'Slug Copied'
                        : 'Click to copy the Slug ID'
                    }
                  >
                    <Link
                      sx={{
                        fontSize: '1rem',
                        transform: 'rotateZ(-45deg)',
                        marginLeft: '5px',
                        cursor: 'pointer'
                      }}
                      onClick={() => {
                        navigator.clipboard.writeText(this.props.env.slug);
                        this.setState({ textCopied: true });
                        setTimeout(() => {
                          this.setState({ textCopied: false });
                        }, 2000);
                      }}
                    />
                  </Tooltip>
                )}
              </InputAdornment>
            )
          }}
        />
        <textarea
          ref={el => (this._descriptionInput = el)}
          className="env-info-input"
          style={{ marginBottom: 10, flex: 1 }}
          type="text"
          placeholder="No Description"
          spellCheck="false"
          rows="4"
          disabled={
            this.state.isOwner ? (this.state.editOpen ? false : true) : true
          }
        />

        {this.props.env.installed && this.renderQuantumJobsToggle()}
        <Box
          display="flex"
          flexDirection="row"
          flexWrap="wrap"
          gap={0.5}
          paddingX="10px"
          paddingBottom="10px"
        >
          {this.state.tags.map((tag, index) => (
            <Chip
              key={index}
              label={tag}
              size="small"
              variant="filled"
              onDelete={
                tag.toLowerCase() === 'custom'
                  ? ''
                  : this.state.editOpen
                    ? () => this.handleRemoveTags(index)
                    : ''
              }
            />
          ))}
          {this.state.isOwner && this.state.editOpen && this.renderAddTags()}
        </Box>
        {this.state.canModify && (
          <Stack flexDirection="row" gap={1} justifyContent="flex-end">
            {!this.state.saveSuccess ? (
              <Tooltip
                title={this.state.editOpen ? 'Turn Edit off' : 'Edit'}
                arrow
                placement="left"
              >
                <IconButton
                  size="small"
                  variant="slide"
                  color="text.secondary"
                  onClick={
                    this.state.editOpen
                      ? () => this.handleEditStateClose()
                      : () => this.handleEditStateOpen()
                  }
                >
                  {this.state.editOpen ? (
                    <EditOff fontSize="inherit" color="inherit" />
                  ) : (
                    <Edit fontSize="inherit" color="inherit" />
                  )}
                </IconButton>
              </Tooltip>
            ) : (
              <ConfirmIcon
                width="2em"
                height="2em"
                color="green"
                style={{ paddingRight: '8px' }}
              />
            )}
            {this.state.editOpen && (
              <Tooltip title="Save" arrow placement="top">
                <IconButton
                  size="small"
                  variant="slide"
                  color="text.secondary"
                  disabled={this.state.saveLoading}
                  onClick={this.handleSubmit}
                >
                  {this.state.saveLoading ? (
                    <Loading />
                  ) : (
                    <SaveOutlined fontSize="inherit" />
                  )}
                </IconButton>
              </Tooltip>
            )}
          </Stack>
        )}
      </div>
    );
  };

  handleGenerateAccessKey = environementId => {
    this.setState({ accessKeyLoading: true });
    this.context
      .getActions('EnvironmentActions')
      .generateAccessKey(environementId)
      .then(res => {
        this.setState({ accessKey: res?.body?.accessKey });
        const shareData = {
          environmentId: environementId,
          overwrite: true,
          isAccessKeyEnv: true
        };
        this.context
          .getActions('EnvironmentActions')
          .shareEnvironment(shareData)
          .then(_res => this.setState({ accessKeyLoading: false }))
          .catch(err => {
            console.log(err);
            this.setState({ accessKeyLoading: false });
          });
      })
      .catch(err => {
        console.log(err);
        this.setState({ accessKeyLoading: false });
      });
  };

  renderSharingPane = () => {
    const handleEnvShare = () => {
      this.setState({ shareEmailApiError: '' });
      if (this.state.shareEmail === '') {
        this.setState({ shareEmailError: 'Email is required' });
        return;
      } else if (!this.state.isCustom) {
        this.setState({
          shareEmailError: 'Only custom environment can be shared',
          sharePopupOpen: true,
          sharePopupMsg: {
            msg: 'Only custom environment can be shared',
            type: 'error'
          }
        });
        return;
      } else if (
        this.state.uninstalling ||
        this.state.cancelling ||
        this.state.deleting ||
        this.props.installing ||
        this.props.packageInstallingEnv === this.props.env._id
      ) {
        this.setState({
          shareEmailError: 'Blocked during state transition',
          sharePopupOpen: true,
          sharePopupMsg: {
            msg: 'Blocked during state transition',
            type: 'error'
          }
        });
        return;
      } else if (this.state.shareEmailError !== '') {
        return;
      } else if (this.state.isShareNode) {
        this.setState({ shareEmailBtnDis: true });
        this.shareEnvironment(false);
      } else {
        this.setState({ upgradePopUp: true });
      }
    };

    const handleOptionChange = (e, newValue) => {
      this.setState({ optionValue: newValue });
    };

    const handleEmailChange = (e, newValue) => {
      this.setState(() => ({ shareEmail: newValue, shareEmailApiError: '' }));
      if (newValue === '') {
        this.setState({ shareEmailError: '' });
      } else if (
        !newValue?.match(/^[A-Za-z\._\-[0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$/)
      ) {
        this.setState({ shareEmailError: 'Invalid email format' });
      } else {
        this.setState({ shareEmailError: '' });
      }
    };

    // makes a new color from a string
    const stringToColor = string => {
      let hash = 0;
      let i;

      /* eslint-disable no-bitwise */
      for (i = 0; i < string?.length; i += 1) {
        hash = string.charCodeAt(i) + ((hash << 5) - hash);
      }

      let color = '#';

      for (i = 0; i < 3; i += 1) {
        const value = (hash >> (i * 8)) & 0xff;
        color += `00${value.toString(16)}`.slice(-2);
      }
      /* eslint-enable no-bitwise */

      return color;
    };

    const stringAvatar = name => {
      return {
        sx: {
          bgcolor: stringToColor(name),
          width: '26px',
          height: '26px',
          fontSize: '18px'
        },
        children: `${name?.slice(0, 1)?.toUpperCase()}`
      };
    };

    const handleCopyAccessKey = () => {
      this.setState({ copyCooldown: true });
      navigator.clipboard.writeText(this.state.accessKey);
      setTimeout(() => this.setState({ copyCooldown: false }), 1500);
    };

    const handleAccessKeyVisibility = () => {
      this.setState(prevState => ({
        accessKeyVisibility: !prevState.accessKeyVisibility
      }));
    };

    const handleReShareEnv = () => {
      this.setState({ resharePopUp: false });
      this.setState({ shareEmailBtnDis: true });
      this.shareEnvironment(true);
    };

    const handleCancelReShareEnv = () => {
      this.setState({
        resharePopUp: false,
        shareEmail: '',
        shareEmailBtnDis: false
      });
    };

    const handleOpenSharingDialog = () => {
      this.setState({
        resharePopUp: true,
        resharePopUpContent: {
          content: 'accessCode',
          title: 'Are you sure?',
          body: 'Generating a new access code will invalidate the current code, and update the global shared copy of this environment.'
        }
      });
    };

    const handleRegenerateAccessKey = () => {
      this.setState({
        resharePopUp: false,
        accessKey: ''
      });
      this.handleGenerateAccessKey(this.props.env._id);
    };

    const handleCancelRegenrateAccessKey = () => {
      this.setState({
        resharePopUp: false,
        resharePopUpContent: {
          content: '',
          title: '',
          body: ''
        }
      });
    };

    const actions = {
      accessCode: {
        confirm: handleRegenerateAccessKey,
        cancel: handleCancelRegenrateAccessKey
      },
      reShareEnv: {
        confirm: handleReShareEnv,
        cancel: handleCancelReShareEnv
      }
    };

    return (
      <div
        className="env-editor-pane"
        id="sharing-pane"
        style={{ marginTop: '0px !important' }}
      >
        <p className="env-editor-pane-title">Share Environment</p>

        <Box className="env-pane-content" flex={1} mt={0}>
          {this.state.isCustom &&
            this.state.isOwner &&
            this.state.isInstalled &&
            this.state.isMount && (
              <Typography fontSize={14}>
                Enable other qBraid users to discover this environment and
                install a copy into their own Lab instance.
              </Typography>
            )}
          {this.state.isMount ? (
            this.state.isOwner ? (
              this.state.isCustom ? (
                this.state.isInstalled ? (
                  <Grid
                    container
                    justifyContent="space-between"
                    alignItems="flex-start"
                    position="relative"
                    spacing={1}
                    mt={1}
                  >
                    <Grid
                      item
                      container
                      xs={12}
                      spacing={1}
                      position="relative"
                    >
                      <Grid item xs={12} sm={12} md={8} lg={8}>
                        <Autocomplete
                          id="env-email-input"
                          size="small"
                          fullWidth
                          freeSolo
                          options={this.state.recentEmails}
                          value={this.state.optionValue}
                          onChange={handleOptionChange}
                          renderOption={(props, option) => (
                            <Stack
                              component="li"
                              flexDirection="row"
                              gap={2}
                              py={3}
                              {...props}
                            >
                              <Avatar {...stringAvatar(option)} />
                              <Typography fontSize={14} color="text.primary">
                                {option}
                              </Typography>
                            </Stack>
                          )}
                          inputValue={this.state.shareEmail}
                          onInputChange={handleEmailChange}
                          renderInput={params => (
                            <TextField
                              {...params}
                              error={this.state.shareEmailError}
                              helperText={
                                (this.state.shareEmail.length > 2 &&
                                  this.state.shareEmailError) ||
                                ' '
                              }
                              placeholder="Enter qBraid user email"
                            />
                          )}
                          sx={{
                            '& .MuiOutlinedInput-root.MuiInputBase-sizeSmall': {
                              fontSize: '14px'
                            }
                          }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={12} md={4} lg={4}>
                        <Button
                          fullWidth
                          className="env-editor-pane-action"
                          onClick={handleEnvShare}
                          style={{
                            background: this.state.shareSuccess
                              ? 'green'
                              : '#673AB7',
                            cursor: this.state.shareEmailBtnDis
                              ? 'not-allowed !important'
                              : 'pointer !important',
                            marginBottom:
                              this.state.shareEmail?.length > 2 &&
                              !this.state.shareEmail.match(
                                /^[A-Za-z\._\-[0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$/
                              )
                                ? '25px'
                                : '0px'
                          }}
                          disabled={this.state.shareEmailBtnDis}
                          size="small"
                          startIcon={
                            this.state.shareSuccess ? (
                              <Check color="green" />
                            ) : (
                              <Send sx={{ transform: 'rotateZ(-45deg)' }} />
                            )
                          }
                        >
                          {this.state.shareSuccess ? 'Sent' : 'Share'}
                        </Button>
                      </Grid>
                      <Grid item xs={12} position="absolute" bottom="4px">
                        {this.state.isCustom &&
                          this.state.isOwner &&
                          this.state.isInstalled &&
                          this.state.isMount &&
                          this.state.shareEmailApiError && (
                            <p className="env-pane-email-error">
                              {this.state.shareEmailApiError}
                            </p>
                          )}
                        {this.state.isCustom &&
                          this.state.isOwner &&
                          this.state.isInstalled &&
                          this.state.isMount &&
                          this.state.shareSuccess && (
                            <p className="env-pane-email-success">
                              Environment shared succesfully...
                            </p>
                          )}
                      </Grid>
                    </Grid>
                    <Grid item xs={12}>
                      <Divider textAlign="center">OR</Divider>
                    </Grid>
                    <Grid
                      item
                      display="flex"
                      justifyContent="center"
                      alignItems="center"
                      xs={12}
                    >
                      {this.state.accessKey === '' ? (
                        <Button
                          fullWidth
                          variant="outlined"
                          color="success"
                          onClick={() =>
                            this.handleGenerateAccessKey(this.props.env._id)
                          }
                          sx={{
                            textTransform: 'none',
                            fontSize: 12,
                            cursor: this.state.accessKeyLoading
                              ? 'progress'
                              : 'pointer'
                          }}
                          disabled={this.state.accessKeyLoading}
                        >
                          {this.state.accessKeyLoading
                            ? 'Generating ...'
                            : 'Generate Access Code'}
                        </Button>
                      ) : (
                        <Grid item xs={12}>
                          <Paper
                            elevation={0}
                            sx={theme => ({
                              display: 'flex',
                              alignItems: 'center',
                              width: '100%',
                              backgroundColor: `${theme.palette.success.light}30`
                            })}
                          >
                            <Typography fontSize={12} color="success" px={1.5}>
                              Share via access code
                            </Typography>
                            <Divider
                              orientation="vertical"
                              sx={{ m: 0.5, height: 28 }}
                            />
                            <InputBase
                              size="small"
                              sx={{
                                ml: 1,
                                flex: 1,
                                fontSize: 12,
                                fontWeight: 600,
                                '&.MuiInputBase-input': {
                                  p: 0
                                }
                              }}
                              value={this.state.accessKey}
                              type={
                                !this.state.accessKeyVisibility
                                  ? 'password'
                                  : 'text'
                              }
                            />
                            <IconButton
                              size="small"
                              onClick={handleAccessKeyVisibility}
                            >
                              {!this.state.accessKeyVisibility ? (
                                <Visibility fontSize="inherit" />
                              ) : (
                                <VisibilityOff fontSize="inherit" />
                              )}
                            </IconButton>
                            <Divider
                              orientation="vertical"
                              sx={{ m: 0.5, height: 28 }}
                            />
                            <Tooltip arrow placement="left" title="Copy">
                              <IconButton
                                size="small"
                                sx={{ mx: 1.5 }}
                                onClick={handleCopyAccessKey}
                              >
                                {this.state.copyCooldown ? (
                                  <ConfirmIcon color="green" />
                                ) : (
                                  <ContentCopy fontSize="inherit" />
                                )}
                              </IconButton>
                            </Tooltip>
                          </Paper>
                        </Grid>
                      )}
                    </Grid>
                    <Grid
                      item
                      xs={12}
                      display="flex"
                      justifyContent="flex-end"
                      alignItems="center"
                      gap={1}
                    >
                      {this.state.accessKey !== '' && (
                        <>
                          <Button
                            variant="text"
                            color="success"
                            size="small"
                            startIcon={<Refresh fontSize="inherit" />}
                            sx={{
                              padding: '0px !important',
                              textTransform: 'none'
                            }}
                            onClick={handleOpenSharingDialog}
                          >
                            Regenerate access code?
                          </Button>
                          <Tooltip
                            title={
                              <React.Fragment>
                                {
                                  'The existing access code will be invalidated and your current environment will replace the global shared copy.'
                                }
                              </React.Fragment>
                            }
                            PopperProps={{
                              sx: theme => ({
                                [`& .${tooltipClasses.tooltip}`]: {
                                  background:
                                    theme.palette.background.alternate,
                                  color: theme.palette.text.primary,
                                  fontSize: 12,
                                  boxShadow: theme.shadows[10]
                                }
                              })
                            }}
                          >
                            <InfoOutlined
                              fontSize="small"
                              color="action"
                              sx={{ width: 14, height: 14 }}
                            />
                          </Tooltip>
                        </>
                      )}
                    </Grid>
                  </Grid>
                ) : (
                  <Grid container>
                    <Grid item xs={12}>
                      <p className="env-pane-prompt">
                        To share an environment, it must be installed. To
                        install this environment, click <b>Install</b> in the
                        panel drop-down.
                      </p>
                    </Grid>
                  </Grid>
                )
              ) : (
                <Grid container>
                  <Grid item xs={12}>
                    <p className="env-pane-prompt">
                      This environment is not shareable. To create a shareable,
                      custom environment, click{' '}
                      <b>Add {'→'} Create Environment</b> in the environments
                      sidebar.
                    </p>
                  </Grid>
                </Grid>
              )
            ) : (
              <Grid container>
                <Grid item xs={12}>
                  <p className="env-pane-prompt">
                    To share an environment, you must be the environment owner.
                    To create your own shareable, custom environment, click{' '}
                    <b>Add {'→'} Create Environment</b> in the environments
                    sidebar.
                  </p>
                </Grid>
              </Grid>
            )
          ) : (
            <Grid container>
              <Grid item xs={12}>
                <p className="env-pane-prompt">
                  Sharing environments is only available within the cloud-based
                  qBraid Lab platform. Launch an instance at{' '}
                  <a
                    href="https://lab.qbraid.com"
                    style={{ color: 'blue' }}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    lab.qbraid.com
                  </a>{' '}
                  to share environments with other users.
                </p>
              </Grid>
            </Grid>
          )}

          {/* {this.renderShareMsg(this.state.sharePopupMsg)} */}
          {this.renderReshareEnvModal({ action: actions })}
          {this.renderUpgradeEnvModal()}
        </Box>
      </div>
    );
  };
  // upgrade modal for share node
  renderUpgradeEnvModal = () => {
    return (
      <Modal
        open={this.state.upgradePopUp}
        onClose={() => this.setState({ upgradePopUp: false })}
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '1em',
          zIndex: '1301'
        }}
      >
        <Grid
          container
          sx={{
            width: '700px',
            minWidth: '200px',
            minHeight: '150px',
            padding: '1em'
          }}
          className="env-pane-re-share"
        >
          <Grid item xs={12}>
            <h3 style={{ margin: '0px' }}>Upgrade to Continue</h3>
          </Grid>
          <Grid item xs={12}>
            <p className="env-pane-email-normal">{`Upgrade your account to unlock premium environment manager features.`}</p>
          </Grid>
          <Grid
            item
            container
            xs={12}
            sx={{
              display: 'flex',
              justifyContent: 'flex-end',
              alignItems: 'center',
              gap: '10px'
            }}
          >
            <Grid item xs={3} sm={3} md={2} lg={2} xl={2}>
              <Button
                variant="slide"
                type="decline"
                fullWidth
                sx={{ textTransform: 'none', minWidth: '120px' }}
                onClick={() => this.setState({ upgradePopUp: false })}
              >
                Maybe later
              </Button>
            </Grid>
            <Grid item xs={2}>
              <Button
                variant="slide"
                sx={{
                  textTransform: 'none',
                  minWidth: '120px'
                }}
                fullWidth
                onClick={() => window.open(`${ACCOUNT_URL}/billing`, '_blank')}
              >
                Upgrade
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Modal>
    );
  };
  // resharing modal for environment sharing
  renderReshareEnvModal = ({ action }) => {
    return (
      <Modal
        open={this.state.resharePopUp}
        onClose={() =>
          this.setState({
            resharePopUp: false,
            shareEmailBtnDis: false,
            shareEmail: ''
          })
        }
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '1em',
          zIndex: '1301'
        }}
      >
        <Grid
          container
          sx={{
            width: '700px',
            minWidth: '200px',
            minHeight: '150px',
            padding: '1em'
          }}
          className="env-pane-re-share"
          spacing={1}
        >
          <Grid item xs={12}>
            <Typography fontSize={18} fontWeight={600} color="text.primary">
              {this.state.resharePopUpContent.title}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography fontSize={14} color="text.primary">
              {this.state.resharePopUpContent.body}
            </Typography>
          </Grid>
          <Grid
            item
            container
            xs={12}
            justifyContent="flex-end"
            alignItems="center"
            spacing={1}
          >
            <Grid item>
              <Button
                variant="slide"
                type="decline"
                sx={{ textTransform: 'none', minWidth: '120px' }}
                onClick={action[this.state.resharePopUpContent.content]?.cancel}
              >
                Cancel
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="slide"
                sx={{
                  textTransform: 'none',
                  minWidth: '120px'
                }}
                onClick={
                  action[this.state.resharePopUpContent.content]?.confirm
                }
              >
                Confirm
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Modal>
    );
  };
  // snack bar for share environment.
  renderShareMsg = () => {
    return (
      <Snackbar
        open={this.state.sharePopupOpen}
        autoHideDuration={2500}
        onClose={this.handleSharePopupClose}
        sx={{
          position: 'sticky',
          width: '300px',
          bottom: '10px!important',
          left: '40px!important'
        }}
      >
        <Alert
          severity={this.state.sharePopupMsg.type}
          variant="filled"
          sx={{
            position: 'absolute',
            width: '100%',
            fontSize: '14px',
            bottom: '10px'
          }}
        >
          {this.state.sharePopupMsg.msg}
        </Alert>
      </Snackbar>
    );
  };

  renderCollaboratorRows = () => {
    let filterRow = [
      <tr key={-1} style={{ borderColor: '#ececec' }}>
        <td className="env-table-filter">
          <input
            placeholder="Filter..."
            onChange={this.handleChangeCollaboratorFilter}
          />
        </td>
        <td></td>
        <td></td>
      </tr>
    ];
    let collabRows = this.state.readAccessUsers
      .concat(
        this.state.writeAccessUsers.map(user => {
          user.write = true;
          return user;
        })
      )
      .filter(user =>
        !this.state.collaboratorFilter
          ? true
          : user.jupyterUsername
              .toLowerCase()
              .indexOf(this.state.collaboratorFilter) !== -1
      )
      .sort((user1, user2) =>
        user1.jupyterUsername.toLowerCase() >
        user2.jupyterUsername.toLowerCase()
          ? 1
          : -1
      )
      .map((user, index) => (
        <tr
          key={user.jupyterUsername + index}
          style={{ borderColor: '#ececec' }}
        >
          <td style={{ width: 180, maxWidth: 180 }}>{user.jupyterUsername}</td>
          <td style={{ width: 70, textAlign: 'center' }}>
            <input type="checkbox" disabled={true} checked={true} />
          </td>
          <td style={{ width: 70, textAlign: 'center' }}>
            <input
              type="checkbox"
              defaultChecked={user.write}
              onChange={() => this.toggleWriteAccess(user)}
            />
          </td>
        </tr>
      ));
    return filterRow.concat(collabRows);
  };

  renderPackagesPane = () => {
    let pkgCount = this.state.packagesInImage.length;

    const calculateHeight = () => {
      // calculates the height of package pane by adding the height of left-side general info and sharing pane
      // **this function can be replaced with static value of "360" if performance is impacted but height of the pane will be impacted**
      const heightOfGeneralInfoPane =
        document.getElementById('general-info-pane')?.offsetHeight;
      const heightOfSharingPane =
        document.getElementById('sharing-pane')?.offsetHeight;
      const calculatedHeight =
        Number(+heightOfGeneralInfoPane + +heightOfSharingPane) - 137; // substracting padding + margin + button height
      switch (true) {
        case !this.props.env.installed:
          return '60vh';
        case calculatedHeight > 480:
          return 360;
        case calculatedHeight === NaN:
          return 310;
        default:
          return calculatedHeight;
      }
    };

    return (
      <div className="env-editor-pane">
        <p className="env-editor-pane-title">Packages</p>
        <div className="env-pane-content" style={{ flex: 1 }}>
          <Box
            sx={theme => ({
              overflow: 'hidden',
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 2
            })}
          >
            <TableContainer
              sx={{
                // maxHeight: this.props.env.installed ? 380 : 410,
                maxHeight: '60vh',
                height: calculateHeight(),
                minHeight: 310,
                position: 'relative',
                backgroundColor: 'var(--jp-layout-color1)',
                overflowY: 'auto',
                overflowX: 'hidden',
                flex: 1
              }}
              component={Paper}
            >
              <Table stickyHeader size="small">
                <TableHead sx={{ color: 'var(--jp-ui-font-color0)' }}>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Version</TableCell>
                    {this.props.env.installed && <TableCell>Remove</TableCell>}
                  </TableRow>
                  {pkgCount > 0 && !this.state.addPackageDialogOpen && (
                    <TableRow>
                      <TableCell colSpan={3} sx={{ top: '37px' }}>
                        <div className="env-pane-search-container">
                          <div className="env-pane-searchbox">
                            <input
                              style={{ width: '100%' }}
                              placeholder="Search packages..."
                              onChange={e =>
                                this.handleChangePackageFilter(e, false)
                              }
                              className="env-pane-input-bar"
                            />
                          </div>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                  {this.state.addPackageDialogOpen && (
                    <TableRow sx={{ position: 'relative', zIndex: 100 }}>
                      <TableCell colSpan={3} sx={{ top: '37px' }}>
                        {this.renderSeachPackagePane()}
                      </TableCell>
                    </TableRow>
                  )}
                </TableHead>

                <TableBody>
                  {pkgCount === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3}>
                        <p
                          className="env-pane-prompt"
                          style={{ textAlign: 'center' }}
                        >
                          No packages have been added to this environment
                        </p>
                      </TableCell>
                    </TableRow>
                  ) : (
                    !this.props.packageLoading &&
                    this.state.packagesInImage
                      .filter(pkg =>
                        !this.state.packageFilter
                          ? true
                          : pkg
                              .split('=')[0]
                              .toLowerCase()
                              .trim()
                              .indexOf(this.state.packageFilter) !== -1
                      )
                      .sort((pkg1, pkg2) =>
                        pkg1.toLowerCase() > pkg2.toLowerCase() ? 1 : -1
                      )
                      .map((pkg, _index) => {
                        let nameAndVersion = pkg.split('==');
                        let name = nameAndVersion[0],
                          version = nameAndVersion[1];
                        return (
                          <TableRow
                            key={name}
                            sx={{
                              '&:last-child td, &:last-child th': { border: 0 }
                            }}
                          >
                            <TableCell component="th" scope="row">
                              {name}
                            </TableCell>
                            <TableCell
                              sx={{
                                wordBreak: 'break-word',
                                wordWrap: 'break-word',
                                overflowWrap: 'break-word',
                                textWrap: 'balance'
                              }}
                            >
                              {version}
                            </TableCell>
                            {this.props.env.installed && (
                              <TableCell
                                sx={{ textAlign: 'right', color: 'indianred' }}
                              >
                                <Tooltip
                                  title="Remove package"
                                  arrow
                                  placement="right"
                                >
                                  <IconButton
                                    size="small"
                                    color={'error'}
                                    disabled={
                                      this.props.installing ||
                                      this.props.env.isPreInstalled ||
                                      this.state.lockedEnv
                                    }
                                    onClick={() => {
                                      !this.props.installing &&
                                        !this.props.env.isPreInstalled &&
                                        this.handleRemovePkg(pkg);
                                    }}
                                  >
                                    <Close />
                                  </IconButton>
                                </Tooltip>
                              </TableCell>
                            )}
                          </TableRow>
                        );
                      })
                  )}

                  {(this.props.packageLoading ||
                    this.state.packageListLoading) &&
                    Array.from({ length: 4 }, (_, i) => i + 1).map(item => (
                      <TableRow key={item}>
                        <TableCell colSpan={3}>
                          <Skeleton variant="text" />
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            {this.renderPopupMsg(this.state.popupMsg)}
          </Box>

          {!this.state.addPackageDialogOpen && this.props.env.installed && (
            <div
              className="env-pane-button-group"
              style={{ paddingTop: 10, paddingBottom: 5 }}
            >
              <button
                className={`env-pane-button ${
                  this.state.pkgListBusy || this.props.env.isPreInstalled
                    ? 'disabled'
                    : 'filled'
                }`}
                onClick={
                  !this.props.env.isPreInstalled && this.openAddPackageDialog
                }
                disabled={
                  this.state.pkgListBusy || this.props.env.isPreInstalled
                }
              >
                + Add a package
              </button>
            </div>
          )}
          {this.state.addPackageDialogOpen && this.props.env.installed && (
            <div
              className="env-pane-button-group"
              style={{ paddingTop: 10, paddingBottom: 5 }}
            >
              <Tooltip
                title="Click to return back"
                open={this.state.packageNotInList}
                arrow={true}
                placement="top"
                componentsProps={{
                  tooltip: {
                    sx: {
                      color: 'white',
                      bgcolor: '#673ab7',
                      '& .MuiTooltip-arrow': {
                        color: '#673ab7'
                      }
                    }
                  }
                }}
              >
                <button
                  className="env-pane-button outlined"
                  onClick={this.closeAddPackageDialog}
                >
                  Cancel
                </button>
              </Tooltip>
              <Tooltip
                title="Click to Add Package"
                open={this.state.packageNotInList}
                arrow={true}
                placement="top"
                componentsProps={{
                  tooltip: {
                    sx: {
                      color: 'white',
                      bgcolor: '#673ab7',
                      '& .MuiTooltip-arrow': {
                        color: '#673ab7'
                      }
                    }
                  }
                }}
              >
                <button
                  className={`env-pane-button ${
                    _.isEmpty(this.state.selectedPkg) || this.props.installing
                      ? 'disabled'
                      : 'filled'
                  }`}
                  onClick={() =>
                    this.handleAddPackageToList(
                      this.state.selectedPkg?.info?.name +
                        this.state.selectedOperator +
                        this.state.selectedPkgVersion
                    )
                  }
                  disabled={
                    _.isEmpty(this.state.selectedPkg) || this.props.installing
                  }
                >
                  + Add
                </button>
              </Tooltip>
            </div>
          )}
        </div>
      </div>
    );
  };

  renderSeachPackagePane = () => {
    const MIN_INPUT_LENGTH = 3;
    return (
      <div className="env-pane-search-container env-edior-slide-in-top">
        <div className="env-pane-searchbox">
          <input
            type="text"
            name="searchbar"
            value={this.state.searchInput}
            className="env-pane-input-bar"
            placeholder="Add package..."
            onChange={this.handleInputChanges}
            onKeyDown={this.handleEnterKeypress}
            autoFocus
          />
          <Tooltip
            title="Click to Search Packages"
            open={this.state.packageNotInList}
            arrow={true}
            placement="top"
            componentsProps={{
              tooltip: {
                sx: {
                  color: 'white',
                  bgcolor: '#673ab7',
                  '& .MuiTooltip-arrow': {
                    color: '#673ab7'
                  },
                  marginBottom: '-8px !important'
                }
              }
            }}
          >
            <div
              onClick={this.handleSearchSubmit}
              className={`${
                this.state.searchInput.length >= MIN_INPUT_LENGTH
                  ? 'shake-bottom'
                  : ''
              }`}
            >
              <SearchIcon
                color={`${
                  this.state.searchInput.length >= MIN_INPUT_LENGTH
                    ? '#673ab7'
                    : '#ABABAB'
                }`}
              />
            </div>
          </Tooltip>
        </div>
        {_.isEmpty(this.state.searchResults) &&
          this.state.isDropdownVisible &&
          this.renderErrorDropdown()}
        {!_.isEmpty(this.state.searchResults) &&
          this.state.isDropdownVisible &&
          this.renderDropdown()}
        {this.state.packageNotInList && this.renderAlertDropDown()}
      </div>
    );
  };

  renderDropdown = () => {
    const operators = ['==', '~=', '<', '<=', '>', '>='];
    return (
      <div className="env-pane-dropdown slide-in-top">
        <ul className="env-pane-dropdown-list">
          <li
            className={`${
              this.state.selectedPkg?.last_serial ===
              this.state.searchResults?.last_serial
                ? 'filled'
                : ''
            }`}
            onClick={() => this.handleSelectPackage(this.state.searchResults)}
          >
            <WhiteCube
              width="34"
              height="36"
              filter={`${
                this.state.selectedPkg?.last_serial ===
                this.state.searchResults?.last_serial
                  ? 'drop-shadow(2px 4px 6px rgba(0,0,0,0.2))'
                  : ''
              }`}
            />
            <span className="env-pane-flexrow">
              <p className="env-pane-dropdown-name">
                {this.state.searchResults?.info?.name}
              </p>
              {/* selectedPkgVersion */}
              <p className="env-pane-dropdown-version">
                <select
                  className="operator-selector"
                  name="operatorSelector"
                  value={this.state.selectedOperator}
                  disabled={this.state.selectedPkgVersion === 'any'}
                  onChange={e =>
                    this.setState({ selectedOperator: e.target.value })
                  }
                >
                  {operators.map(operator => (
                    <option value={operator}>{operator}</option>
                  ))}
                </select>
              </p>
              <p className="env-pane-dropdown-version">
                {/* {this.state.searchResults?.info?.version} */}
                <select
                  style={{
                    fontWeight: '600',
                    width: '70px',
                    padding: '.3em',
                    border:
                      this.state.selectedPkg?.last_serial ===
                      this.state.searchResults?.last_serial
                        ? '1px solid white'
                        : '1px solid #673ab7',
                    backgroundColor:
                      this.state.selectedPkg?.last_serial ===
                      this.state.searchResults?.last_serial
                        ? '#ffffff'
                        : '#673ab7',
                    borderRadius: '5px',
                    color:
                      this.state.selectedPkg?.last_serial ===
                      this.state.searchResults?.last_serial
                        ? '#673ab7'
                        : '#ffffff'
                  }}
                  className="package-selector"
                  name="packageVersion"
                  id="packageVersion"
                  value={this.state.selectedPkgVersion}
                  onChange={e => {
                    this.setState({ selectedPkgVersion: e.target.value });
                    if (e.target.value === 'any') {
                      this.setState({ selectedOperator: operators[0] });
                    }
                  }}
                >
                  <option value="any">Any</option>
                  {this.state.availableVersions?.map(version => {
                    return <option value={version}>{version}</option>;
                  })}
                </select>
              </p>
            </span>
          </li>
        </ul>
      </div>
    );
  };

  renderErrorDropdown = () => {
    return (
      <div className="env-pane-dropdown slide-in-top">
        <ul className="env-pane-dropdown-list">
          <li>
            <WhiteCube width="34" height="36" />
            <span className="env-pane-flexrow">
              <p className="env-pane-dropdown-name">No package found!</p>
            </span>
          </li>
        </ul>
      </div>
    );
  };
  renderAlertDropDown = () => {
    return (
      <div className="env-pane-dropdown slide-in-top">
        <ul className="env-pane-dropdown-list">
          <li className="env-pane-dropdown-over-ride">
            <InfoOutlined width="34" height="36" />
            <span>
              <p style={{ fontSize: '12px', fontWeight: '400' }}>
                The package is not installed, once query is completed, press the{' '}
                <b style={{ color: '#673ab7' }}>"Enter"</b> key or{' '}
                <b style={{ color: '#673ab7' }}>"Search Icon"</b> to retrieve
                the package
              </p>
            </span>
          </li>
        </ul>
      </div>
    );
  };

  renderPopupMsg = ({ msg, type }) => {
    return (
      <Snackbar
        open={this.state.popupOpen}
        autoHideDuration={2500}
        onClose={this.handlePopupClose}
        sx={{ position: 'sticky', width: '300px', bottom: '10px' }}
      >
        <Alert
          severity={type}
          variant="filled"
          sx={{
            position: 'absolute',
            width: 'calc(100% - 3em)',
            fontSize: '14px',
            bottom: '10px'
          }}
        >
          {msg}
        </Alert>
      </Snackbar>
    );
  };

  renderInstallInfoPane = () => {
    return (
      <Grid item xs={12}>
        <div className="env-editor-pane-new" style={{ minHeight: 150 }}>
          <div className="env-pane-content">
            {this.props.packageInstallingEnv === this.props.env._id ? (
              <Stack sx={{ width: '100%', color: 'grey.500' }} spacing={1}>
                <Typography className="env-pane-prompt">
                  {'Package is being installed'}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={this.props.packageProgress}
                  sx={{
                    backgroundColor: '#edcefd',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#673ab7'
                    }
                  }}
                />
              </Stack>
            ) : (
              <Stack sx={{ width: '100%', color: 'grey.500' }} spacing={1}>
                <Typography className="env-pane-prompt">
                  {this.state.cancelling
                    ? 'Cancelling installation'
                    : 'Environment is being installed/updated'}
                </Typography>
                <LinearProgress
                  sx={{
                    backgroundColor: this.state.cancelling
                      ? 'red'
                      : '#9909e091',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: this.state.cancelling
                        ? 'darkred'
                        : '#673ab7'
                    }
                  }}
                />
              </Stack>
            )}
          </div>
        </div>
      </Grid>
    );
  };

  renderUpdatePane = () => {
    if (this.props.env.isPreInstalled) {
      return null;
    }

    let displayText;

    if (this.state.isCustom) {
      const createdAt = formatUTCDateTime(this.props.env.createdAt);
      const updatedAt = formatUTCDateTime(this.props.env.updatedAt);
      const sharedWith = this.state.readAccessUsers?.length ?? 0;
      const sharedWithText = `${sharedWith} user${sharedWith === 1 ? '' : 's'}`;
      displayText = (
        <Typography fontSize={14} color="text.secondary">
          createdAt: {createdAt} UTC
          <br />
          updatedAt: {updatedAt} UTC
          <br />
          sharedWith: {sharedWithText}
        </Typography>
      );
    } else if (this.props.env.canUpdate) {
      displayText = (
        <Typography fontSize={14} color="text.secondary">
          An updated version of the {this.props.env.displayName} environment is
          available!
        </Typography>
      );
    } else {
      displayText = (
        <Typography fontSize={14} color="text.secondary">
          Your {this.props.env.displayName} environment is up-to-date with the
          latest version.
        </Typography>
      );
    }

    const minHeight = this.state.isInstalled ? 150 : 105;

    const handleOpenAlert = () => {
      this.setState(
        {
          actionAlertContext: {
            content: 'publish',
            title: 'Confirm Environment Publish Request',
            body: 'Are you sure you want to submit your custom environment for review? By requesting to publish, you are agreeing to transfer ownership of your environment to qBraid. If approved, it will be made publicly available for all qBraid Lab users to install. Please confirm your submission or cancel if you wish to make any further changes.',
            confirmButtonText: 'Submit for Review',
            cancelButtonText: 'Cancel'
          }
        },
        () => {
          this.handleActionAlertOpen();
        }
      );
    };

    return (
      <Grid item xs={12}>
        <div className="env-editor-pane-new" style={{ minHeight: minHeight }}>
          <div className="env-pane-content" style={{ gap: '8px' }}>
            <Stack direction="row" alignItems="flex-start" gap={2}>
              {this.props.env.canUpdate ? (
                <Update color="action" fontSize="small" />
              ) : (
                <UpdateDisabled color="action" fontSize="small" />
              )}
              {displayText}
            </Stack>
            {this.state.uninstalling && (
              <Stack gap={1}>
                <Typography className="env-pane-prompt">{`Uninstalling ${this.props.env.displayName}`}</Typography>
                <LinearProgress
                  sx={{
                    backgroundColor: this.state.uninstalling
                      ? 'red'
                      : '#9909e091',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: this.state.uninstalling
                        ? 'darkred'
                        : '#673ab7'
                    }
                  }}
                />
              </Stack>
            )}
          </div>
        </div>
        {this.renderShareMsg()}
      </Grid>
    );
  };

  renderDeletePane = () => {
    return (
      <Grid item xs={12}>
        <div
          className="env-editor-pane-new"
          // style={{ minHeight: 75 }}
        >
          <div className="env-pane-content">
            <p
              className="editor-action-alt"
              style={
                this.state.deleting || this.props.installing
                  ? { backgroundColor: '#b67d7d', cursor: 'not-allowed' }
                  : null
              }
              onClick={
                this.state.deleting || this.props.installing
                  ? null
                  : this.handleDeleteAlertOpen
              }
            >
              <span>
                <img
                  style={{
                    marginRight: 8,
                    height: 14,
                    filter: 'invert(1)'
                  }}
                  src="https://qbraid-static.s3.amazonaws.com/trash.svg"
                />
              </span>
              <span style={{ verticalAlign: 'text-bottom' }}>
                {this.state.deleting ? 'Deleting...' : 'Delete'}
              </span>
            </p>
            <p className="env-pane-prompt">
              Deleting an environment will remove it permanently.
            </p>
          </div>
        </div>
      </Grid>
    );
  };

  renderUninstallPane = () => {
    // if user of the selected user is owner and the current env is uninstalled, show delete pane
    if (!this.props.env.installed && this.state.isOwner) {
      return this.renderDeletePane();
    }
    // hide uninstallation UI if env is not installed, or is the default qbraid env, which is intended to be present at all times
    if (
      this.props.env &&
      (!this.props.env.installed || this.props.env.isPreInstalled)
    ) {
      return null;
    }
    // show uninstall pane
    return (
      <Grid item xs={12}>
        <div
          className="env-editor-pane-new"
          // style={{ minHeight: 150 }}
        >
          <div className="env-pane-content">
            <p
              className="editor-action-alt"
              style={
                this.state.uninstalling || this.props.installing
                  ? { backgroundColor: '#b67d7d', cursor: 'not-allowed' }
                  : null
              }
              onClick={
                this.state.uninstalling || this.props.installing
                  ? null
                  : this.handleUninstallAlertOpen
              }
            >
              <span>
                <img
                  style={{
                    marginRight: 8,
                    height: 14,
                    filter: 'invert(1)'
                  }}
                  src="https://qbraid-static.s3.amazonaws.com/trash.svg"
                />
              </span>
              <span style={{ verticalAlign: 'text-bottom' }}>
                {this.state.uninstalling ? 'Uninstalling...' : 'Uninstall'}
              </span>
            </p>
            <p className="env-pane-prompt">
              Uninstalling an environment will remove it from your file system,
              freeing up disk space, and allow you to reinstall the most
              up-to-date version, if applicable.
            </p>
          </div>
        </div>
      </Grid>
    );
  };

  handleActionAlertOpen = () => {
    this.setState({ actionAlert: true });
  };

  handleActionAlertClose = () => {
    this.setState({
      actionAlert: false,
      actionAlertContext: {
        content: '',
        title: '',
        body: '',
        confirmButtonText: '',
        cancelButtonText: ''
      }
    });
  };

  confirmButtonAction = () => {
    if (this.state.actionAlertContext.content === 'publish') {
      this.requestPublishEnvironment();
      this.handleActionAlertClose();
    }
  };

  cancelButtonAction = () => {
    if (this.state.actionAlertContext.content === 'publish') {
      this.handleActionAlertClose();
    }
  };

  actionAlert = () => {
    return (
      <Dialog
        open={this.state.actionAlert}
        onClose={this.handleActionAlertClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        className="action-alert-dialog-box"
        transitionDuration={100}
      >
        <DialogTitle id="alert-dialog-title">
          {this.state.actionAlertContext.title}
        </DialogTitle>
        <DialogContent id="alert-dialog-content">
          <DialogContentText id="alert-dialog-description">
            {this.state.actionAlertContext.body}
          </DialogContentText>
        </DialogContent>
        <DialogActions id="alert-dialog-actions">
          <Button
            variant="outlined"
            color="error"
            onClick={this.cancelButtonAction}
            sx={{ textTransform: 'none', minWidth: '120px' }}
          >
            {this.state.actionAlertContext.cancelButtonText}
          </Button>
          <Button
            color="secondary"
            variant="contained"
            sx={{
              textTransform: 'none',
              minWidth: '120px'
            }}
            onClick={this.confirmButtonAction}
            autoFocus
            disableFocusRipple
          >
            {this.state.actionAlertContext.confirmButtonText}
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  renderUninstallAlert = () => {
    return (
      <Dialog
        open={this.state.uninstallAlert}
        onClose={this.handleUninstallAlertClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        className="env-unins-dialog-box"
        transitionDuration={100}
      >
        <DialogTitle id="alert-dialog-title">
          {this.state.cancelRequest
            ? 'Confirm Cancellation'
            : 'Confirm Uninstall'}
        </DialogTitle>
        <DialogContent id="alert-dialog-content">
          <DialogContentText id="alert-dialog-description">
            {this.state.cancelRequest
              ? 'Are you sure you want to cancel installing this environment?'
              : 'Are you sure you want to uninstall this environment?'}
          </DialogContentText>
        </DialogContent>
        <DialogActions id="alert-dialog-actions">
          <Button
            variant="slide"
            type="decline"
            onClick={this.handleUninstallAlertClose}
            sx={{ textTransform: 'none', minWidth: '120px' }}
          >
            Cancel
          </Button>
          <Button
            className="env-unins-alert-box-uninstall-button"
            variant="slide"
            sx={{
              textTransform: 'none',
              minWidth: '120px'
            }}
            onClick={this.handleCustomUninstall}
            autoFocus
            disableFocusRipple
          >
            {this.state.cancelRequest ? 'Cancel Installation' : 'Uninstall'}
          </Button>
        </DialogActions>
      </Dialog>
    );
  };
  renderDeleteAlert = () => {
    return (
      <Dialog
        open={this.state.deleteAlert}
        onClose={this.handleDeleteAlertClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        className="env-unins-dialog-box"
        transitionDuration={100}
      >
        <DialogTitle id="alert-dialog-title" fontWeight={600}>
          Are you sure?
        </DialogTitle>
        <DialogContent id="alert-dialog-content">
          <DialogContentText id="alert-dialog-description">
            Proceeding will lead to permanent deletion of environment{' '}
            <b>{this.props.env.displayName}</b>. This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions id="alert-dialog-actions">
          <Button
            variant="slide"
            type="decline"
            onClick={this.handleDeleteAlertClose}
            sx={{ textTransform: 'none', minWidth: '120px' }}
          >
            Cancel
          </Button>
          <Button
            className="env-unins-alert-box-uninstall-button"
            variant="slide"
            sx={{
              textTransform: 'none',
              minWidth: '120px'
            }}
            onClick={this.handleDelete}
            autoFocus
            disableFocusRipple
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  renderCancelInstallPane = () => {
    // hide uninstallation UI if env is not installed, or is the default qbraid env, which is intended to be present at all times
    // Don't allow uninstalling pre-installed environments
    if (this.props.env && this.props.env.isPreInstalled) {
      return null;
    }

    return (
      <Grid item xs={12}>
        <div className="env-editor-pane-new" style={{ minHeight: 150 }}>
          <div className="env-pane-content">
            <Button
              fullWidth
              variant="contained"
              size="medium"
              sx={{
                textTransform: 'none',
                backgroundColor: 'darkred',
                borderRadius: '6px',
                '&:hover': {
                  backgroundColor: 'red'
                }
              }}
              startIcon={<NotInterested />}
              onClick={!this.state.cancelling && this.handleCancelReq}
              disabled={
                this.state.cancelling ||
                this.props.packageInstallingEnv === this.props.env._id
              }
            >
              {this.state.cancelling ? 'Cancelling...' : 'Cancel Installation'}
            </Button>
          </div>
        </div>
      </Grid>
    );
  };
  renderExtraUninsConfirmAlert = () => {
    return (
      <Dialog
        open={this.state.extraUninstallAlert}
        onClose={this.handleExtraUninsConfirmClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        className="env-unins-dialog-box"
        transitionDuration={100}
      >
        <DialogTitle id="alert-dialog-title">{'Are you sure?'}</DialogTitle>
        <DialogContent id="alert-dialog-content">
          <DialogContentText id="alert-dialog-description">
            {`${
              this.state.cancelRequest ? 'Cancelling' : 'Uninstalling'
            } will lead to permanent deletion of environment '${
              env.displayName
            }'${
              this.props.env.readAccessUsers?.length > 0
                ? ' and remove access from all users that it has been shared with'
                : ''
            }. This action cannot be undone.`}
          </DialogContentText>
        </DialogContent>
        <DialogActions id="alert-dialog-actions">
          <Button
            variant="slide"
            type="decline"
            onClick={this.handleExtraUninsConfirmClose}
            sx={{ textTransform: 'none', minWidth: '120px' }}
          >
            Cancel
          </Button>
          <Button
            className="env-unins-alert-box-uninstall-button"
            sx={{
              textTransform: 'none',
              minWidth: '120px'
            }}
            onClick={this.handleUninstall}
            variant="slide"
            autoFocus
            disableFocusRipple
          >
            Permanently Delete
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  renderDialogFooter = () => {
    return this.state.canModify ? (
      <DialogActions
        sx={{
          justifyContent: 'center',
          padding: '10px',
          background: 'linear-gradient(120deg, #35383a 10%, #5e5f61 100%)'
        }}
      >
        <Button
          sx={{
            padding: '0.3rem 2.5rem',
            minWidth: '100px'
          }}
          variant="slide"
          type="decline"
          onClick={() => {
            this.props.onClose();
          }}
        >
          cancel
        </Button>

        <Button
          sx={{
            padding: '0.3rem 2.5rem',
            minWidth: '100px'
          }}
          variant="slide"
          onClick={this.handleSubmit}
        >
          {env ? 'Save' : 'Create'}
        </Button>
      </DialogActions>
    ) : (
      <DialogActions
        sx={{
          justifyContent: 'center',
          padding: '10px',
          background: 'linear-gradient(120deg, #35383a 10%, #5e5f61 100%)'
        }}
      >
        <Button
          sx={{
            padding: '0.3rem 2.5rem',
            minWidth: '100px'
          }}
          variant="slide"
          type="decline"
          onClick={() => {
            this.props.onClose();
          }}
        >
          Close
        </Button>
      </DialogActions>
    );
  };

  render() {
    let { env } = this.props;
    let dark = this.props.darkmode;
    // cancel button was #232c36
    return (
      <Dialog
        fullWidth
        maxWidth="md"
        open={this.state.loaded}
        style={Object.assign(dark ? { backgroundColor: '#464646' } : {})}
        onClose={() => {
          this.props.onClose();
        }}
      >
        <DialogTitle className="editor-header" sx={{ m: 0, p: 2 }}>
          {env ? `${env.displayName} Environment` : 'New environment'}

          <IconButton
            aria-label="close"
            onClick={() => {
              this.props.onClose();
            }}
            sx={{
              position: 'absolute',
              right: 8,
              top: 12
            }}
          >
            <Close />
          </IconButton>
        </DialogTitle>

        <DialogContent
          sx={{
            backgroundColor: 'var(--jp-layout-color2)',
            padding: '16px'
          }}
          dividers
        >
          <Grid container spacing={2}>
            <Grid item container xs={12} md={6} spacing={2}>
              <Grid item xs={12}>
                {this.renderInfoPane()}
              </Grid>

              <Grid item xs={12}>
                {this.renderSharingPane()}
              </Grid>

              {this.props.installing ||
              this.state.cancelling ||
              this.state.cancelRequest
                ? this.renderInstallInfoPane()
                : (this.state.isInstalled || this.state.isCustom) &&
                  this.renderUpdatePane()}
            </Grid>

            <Grid item container xs={12} md={6} spacing={2}>
              <Grid item xs={12}>
                {this.renderPackagesPane()}
              </Grid>
              {this.props.installing ||
              this.state.cancelling ||
              this.state.cancelRequest
                ? this.renderCancelInstallPane()
                : this.renderUninstallPane()}
            </Grid>
          </Grid>
        </DialogContent>
        {this.actionAlert()}
        {this.renderUninstallAlert()}
        {this.renderExtraUninsConfirmAlert()}
        {this.renderDeleteAlert()}
      </Dialog>
    );
  }
}
