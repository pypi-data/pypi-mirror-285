import React, { Component, Fragment } from 'react';

import contextTypes from '../contextTypes';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HttpsIcon from '@mui/icons-material/Https';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import '../../style/EnvironmentTile.css';
import { Box, LinearProgress, Stack, Tooltip, Typography } from '@mui/material';
import { ACCOUNT_URL } from '../actions/ApiActions';
import { Loading } from '../assets/icons/Loading';
import LogoLoader from './LogoLoader';
const INSTALL_ENV_PERMS_NODE = 'qbraid.environments.install';
const QSHARP_ENV_PERMS_NODE = 'qbraid.environments.qsharp';
const premiumEnvPermsNodeMap = {
  qsharp_b54crn: QSHARP_ENV_PERMS_NODE
};

export default class EnvironmentTile extends Component {
  static contextTypes = contextTypes;

  constructor(props, context) {
    super(props, context);
    this.state = {
      collapsed: true,
      lockedTile: true
    };
  }

  static getDerivedStateFromProps(props, state) {
    if (props.environment.installed) {
      const premiumEnvPermsNode =
        premiumEnvPermsNodeMap[props.environment.slug];
      if (premiumEnvPermsNode) {
        if (
          !props.qbUser.user ||
          !props.qbUser.user.permissionsNodes ||
          props.qbUser.user.permissionsNodes.indexOf(premiumEnvPermsNode) === -1
        ) {
          return { ...state, lockedTile: true };
        }
      }
      return { ...state, lockedTile: false };
    } else {
      if (
        !props.qbUser.user ||
        !props.qbUser.user.permissionsNodes ||
        props.qbUser?.user.permissionsNodes?.indexOf(INSTALL_ENV_PERMS_NODE) ===
          -1
      ) {
        let isFree = false;
        props.environment.tags.forEach(tag => {
          if (tag === 'free') {
            isFree = true;
          }
        });
        if (isFree) {
          return { ...state, lockedTile: false };
        } else {
          return { ...state, lockedTile: true };
        }
      } else {
        return { ...state, lockedTile: false };
      }
    }
  }

  toggleCollapsed = envId => {
    const {
      isInstalled,
      packageInstallingEnv,
      environment,
      isInstalling,
      expandedEnvs
    } = this.props;
    const isTileExpanded = expandedEnvs?.includes(envId);
    // environment?.isExpanded ||
    const isInstallingPackage = packageInstallingEnv === envId;
    const isSystemPython = environment.sysPython;

    if (
      !isInstalling &&
      isInstalled &&
      isTileExpanded &&
      !isInstallingPackage &&
      !isSystemPython
    ) {
      this.props.flux
        .getActions('EnvironmentActions')
        .updatePackagesList(envId)
        .catch(err => {
          console.log(
            'Error at update package in toggle collapsed at envTile ',
            err
          );
        });
    }
    this.props.onToggleExpand(envId);
  };

  renderVerifyLoader = () => (
    <Box
      position="absolute"
      width="100%"
      height="100%"
      className="env_verification-loader"
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      gap={3}
      sx={{
        cursor: 'wait'
      }}
    >
      <LogoLoader />
      <Stack flexDirection="row" gap={1}>
        <Loading width={20} height={20} className="env_loader" />
        <Typography fontSize={14} color="text.primary">
          Verifying GPU configuration...
        </Typography>
      </Stack>
    </Box>
  );

  renderTags = () =>
    this.props.environment.tags.map((tag, index) => (
      <p key={index} className="env-tag">
        {tag}
      </p>
    ));

  render() {
    let env = this.props.environment;
    let { user } = this.props.qbUser;
    let tileStyle = {};

    if (this.props.isActive) {
      tileStyle.backgroundColor = '#dad4e7';
      // tileStyle.backgroundImage = 'linear-gradient(130deg, #df0982, #46096f)';
      tileStyle.border = '1px solid #673ab7';
    }
    if (this.state.lockedTile) {
      tileStyle.border = 'none';
    }

    if (
      // env.isExpanded ||
      this.props.isNewEnv ||
      this.props.expandedEnvs?.includes(env._id)
    ) {
      tileStyle.maxHeight = 9999;
      tileStyle.padding = '0 10px 60px 10px';
    } else {
      tileStyle.maxHeight = 0;
      tileStyle.padding = '0 10px 40px 10px';
    }

    return (
      <div className="env-tile" style={{ ...tileStyle }}>
        <div
          className={`env-name flex-box ${
            (this.props.isNewEnv ||
              // env.isExpanded ||
              this.props.expandedEnvs?.includes(env._id)) &&
            'env-name-border'
          }`}
          style={{
            color: this.props.isActive ? 'black' : 'var(--jp-ui-font-color0)'
          }}
        >
          <span
            className="env-tile-display-name flex-box_start"
            style={{
              cursor: 'pointer'
            }}
            onClick={() => this.toggleCollapsed(env._id)}
          >
            {env?.logo &&
            typeof env?.logo === 'object' &&
            !Array.isArray(env?.logo) &&
            env?.logo !== null ? (
              <span
                // style={{ float: 'left', cursor: 'pointer' }}
                onClick={() => this.toggleCollapsed(env._id)}
              >
                <img
                  style={{
                    height: 18,
                    maxWidth: 45,
                    marginRight: 5
                  }}
                  src={
                    this?.props?.isDarkTheme ? env.logo.dark : env.logo.light
                  }
                />
              </span>
            ) : (
              <span
                // style={{ float: 'left', cursor: 'pointer' }}
                onClick={() => this.toggleCollapsed(env._id)}
              >
                <img
                  key={0}
                  style={{
                    height: 18,
                    maxWidth: 45,
                    marginRight: 5
                  }}
                  src={
                    localStorage.getItem(env.displayName) ||
                    this?.props?.isDarkTheme
                      ? env?.logo?.dark
                      : env?.logo?.light
                  }
                />
              </span>
            )}
            <p className="env-tile-display-name">{env.displayName}</p>
            {this.state.lockedTile && (
              <Tooltip
                title={
                  this.props.isInstalled
                    ? 'Upgrade to access environment'
                    : 'Upgrade to install environment'
                }
                arrow
              >
                <HttpsIcon
                  sx={{
                    fontSize: '1rem!important',
                    color: 'var(--jp-ui-font-color0)',
                    marginLeft: '5px',
                    zIndex: '99',
                    cursor: 'pointer'
                  }}
                />
              </Tooltip>
            )}
          </span>

          <span className="env-tile_right-flex-box">
            {this.props.isActive && (
              <span className="env-tile-active-label">active</span>
            )}

            <img
              src={
                env.pinned
                  ? 'https://qbraid-static.s3.amazonaws.com/bookmark-solid-pink.svg'
                  : 'https://qbraid-static.s3.amazonaws.com/bookmark-solid-gray.svg'
              }
              style={{
                width: 15,
                height: 15,
                cursor: this.state.lockedTile ? 'not-allowed' : 'pointer'
              }}
              onClick={() => {
                if (!this.state.lockedTile) {
                  this.props.onTogglePinned(env._id);
                }
              }}
            />

            <ExpandMoreIcon
              sx={{
                fontSize: '1rem!important',
                transform:
                  this.props.isNewEnv ||
                  // env.isExpanded ||
                  this.props.expandedEnvs?.includes(env._id)
                    ? 'rotateX(180deg)'
                    : 'rotateX(0deg)',
                transition: 'transform 300ms ease',
                cursor: 'pointer',
                zIndex: '99'
              }}
              onClick={() => this.toggleCollapsed(env._id)}
            />
          </span>
        </div>
        <span
          style={{
            visibility:
              // env.isExpanded ||
              this.props.isNewEnv || this.props.expandedEnvs?.includes(env._id)
                ? 'visible'
                : 'hidden'
          }}
          // style={{ visibility: this.state.collapsed ? 'hidden' : 'visible' }}
        >
          <div className="env-content">
            {this.props?.verifyLoading?.loading &&
              this.props?.verifyLoading?.envId === env._id &&
              this.renderVerifyLoader()}
            <div className="env-tags">
              <div>{this.renderTags()}</div>
              <div>
                <Tooltip title="Clone" arrow>
                  <ContentCopyIcon
                    onClick={() => {
                      if (!this.state.lockedTile) {
                        this.props.cloneEnvironment(env);
                      }
                    }}
                    sx={{
                      cursor: this.state.lockedTile ? 'not-allowed' : 'pointer',
                      color: 'gray',
                      fontSize: '1.5em'
                    }}
                  />
                </Tooltip>
              </div>
            </div>
            <div className="env-details">
              <p
                className="env-description"
                style={{
                  color: this.props.isActive
                    ? 'rgba(0, 0, 0, 0.54)'
                    : 'var(--jp-ui-font-color2)'
                }}
              >
                {env.description || 'No description'}
              </p>
              {this.props.packageInstallingEnv === env._id &&
              this.props.packageProgress > 0 ? (
                <div>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'flex-start',
                      alignItems: 'center'
                    }}
                  >
                    <img
                      src="https://qbraid-static.s3.amazonaws.com/python.svg"
                      style={{ width: '20px', height: '20px' }}
                    />
                    <p
                      className="env-packages"
                      style={{
                        color: this.props.isActive
                          ? 'black'
                          : 'var(--jp-ui-font-color1)'
                      }}
                    >
                      Installing Packages...
                    </p>
                  </div>
                  <div style={{ marginTop: '5px' }}>
                    <LinearProgress
                      variant="determinate"
                      sx={{
                        backgroundColor: '#edcefd',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: '#673ab7'
                        }
                      }}
                      value={this.props.packageProgress}
                    />
                  </div>
                </div>
              ) : (
                <div className="env-config">
                  <p
                    className="env-packages"
                    style={{
                      color: this.props.isActive
                        ? 'black'
                        : 'var(--jp-ui-font-color1)'
                    }}
                  >
                    <span style={{ verticalAlign: 'middle' }}>
                      {/* src=https://qbraid-static.s3.amazonaws.com/logos/xcpp.png if slug === xcpp_d6z3gv */}
                      <img src="https://qbraid-static.s3.amazonaws.com/python.svg" />
                    </span>
                    <span>{`${env.packagesInImage.length} ${
                      env.packagesInImage.length === 1 ? 'package' : 'packages'
                    }`}</span>
                  </p>
                </div>
              )}
            </div>
          </div>
          <div className="env-actions">
            {this.state.lockedTile ? (
              <p
                className="env-action"
                style={{
                  width: '100%',
                  marginRight: 10,
                  background: '#673AB7',
                  cursor: 'pointer',
                  zIndex: '100'
                }}
                onClick={() => {
                  window.open(`${ACCOUNT_URL}/billing`, '_blank');
                }}
              >
                Upgrade
              </p>
            ) : (
              this.props.activateButton
            )}
            <p
              className={`env-action env-button-outlined ${
                this.props.isActive && 'kernel-activated-button'
              }`}
              onClick={this.props.edit}
            >
              More...
            </p>
          </div>
        </span>
      </div>
    );
  }
}
