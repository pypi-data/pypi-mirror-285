function EnvironmentActions() {
  this.registerAlt = alt => {
    // hack to provide the alt singleton to function-based action creators (necessitated by ES6 breaking class-based action creators in alt by mandating construction via 'new')
    this.alt = alt;
    this.actions = alt.getActions(this.__proto__.constructor.__proto__.name);
  };

  // BEGIN DATA RELAYS. data relays are a special case of actions creators which are pure functions used by standard action creators to pass data retrieved from api calls etc to stores. stores bind listeners to data relays exclusively. data relays are always prefixed with an underscore to easily distinguish them from standard action creators.
  this._updateAll = envs => envs; // passes the master list of environments to EnvironmentStore

  this._registerActivated = env => env; // passes the activated environment to EnvironmentStore

  this._registerInstalling = env => env; // passes the environment currently being installed to EnvironmentStore
  // END DATA RELAYS

  // BEGIN ACTION CREATORS - besides the dispatch line at the start of each handler, all logic and semantics are identical to their equivalen in standard RAMEN.

  this.updateAll = () => {
    // updates the master list of environments
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .get('/environments')
        .end((err, res) => {
          if (err) {
            reject(err);
          } else {
            let envs = res.body;
            if (!envs || !Array.isArray(envs)) {
              envs = [];
            }
            this.actions._updateAll(envs);
            resolve(envs);
          }
        });
    });
  };

  this.fetchAllEnv = () => {
    // updates the master list of environments
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .get('/environments')
        .end((err, res) => {
          if (err) {
            reject(err);
          } else {
            let envs = res.body;
            if (!envs || !Array.isArray(envs)) {
              reject({ error: 'Invalid envs array', envs: envs });
            }
            resolve(envs);
          }
        });
    });
  };

  this.editOne = (environmentId, changes) => {
    // edit an environment
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .put('/environments/' + environmentId)
        .send(changes)
        .end((err, res) => {
          if (err) {
            reject(err);
          } else {
            resolve(res);
          }
        });
    });
  };

  this.toggleActive = environmentId => {
    // activates the environment with the provided environmentId
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      let env = this.alt.getStore('EnvironmentStore').getState()
        .environmentCache[environmentId];
      if (!env) {
        return reject('No environment with id ' + environmentId);
      }

      let installing = this.alt
        .getStore('EnvironmentStore')
        .getState().installingEnvironment;

      if (installing && env.slug === installing.slug) {
        return reject(
          'Cannot activate environment while it is being installed'
        );
      }

      let isActive = env.active;
      let requestBody = { slug: env.slug };

      this.alt
        .getActions('JupyterApiActions')
        .query('toggle-kernel', {
          body: JSON.stringify(requestBody),
          method: 'POST'
        })
        .then(data => {
          if (this.alt.jupyterlab) {
            let kernelSpecManager =
              this.alt.jupyterlab.serviceManager.kernelspecs;
            kernelSpecManager.refreshSpecs().then(() => {
              if (kernelSpecManager.specs.default) {
                this.alt.jupyterlab.serviceManager.sessions._sessionConnections.forEach(
                  sessionConnection => {
                    try {
                      sessionConnection.changeKernel({
                        name: kernelSpecManager.specs.default
                      });
                    } catch (e) {
                      console.error(e);
                    }
                  }
                );
              }
            });
          }
          let allEnvs = this.alt
            .getStore('EnvironmentStore')
            .getState().environments;

          allEnvs = allEnvs.map(env => {
            if (
              env._id === environmentId &&
              // Don't allow deactivation of the default environment
              env.slug !== 'qbraid_000000'
            ) {
              env.active = !isActive;
            }
            return env;
          });
          this.actions._updateAll(allEnvs);
          resolve(data);
        })
        .catch(err => {
          reject(err);
        });
    });
  };

  this.addPinned = environmentId => {
    // add pinned environment to user MongoDB
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .put('/environments/pin/' + environmentId)
        .end((err, res) => {
          if (err) {
            reject(err);
          } else if (res.status !== 200) {
            reject(false);
          } else {
            let allEnvs = this.alt
              .getStore('EnvironmentStore')
              .getState().environments;

            // update pinned
            allEnvs = allEnvs.map(env => {
              if (env._id === environmentId) {
                env.pinned = true;
              }
              return env;
            });

            this.actions._updateAll(allEnvs);
            resolve(allEnvs);
          }
        });
    });
  };

  this.removePinned = environmentId => {
    // remove pinned environment from user MongoDB
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .put('/environments/unpin/' + environmentId)
        .end((err, res) => {
          if (err) {
            reject(err);
          } else if (res.status !== 200) {
            reject(res.status);
          } else {
            let allEnvs = this.alt
              .getStore('EnvironmentStore')
              .getState().environments;

            // update pinned
            allEnvs = allEnvs.map(env => {
              if (env._id === environmentId) {
                env.pinned = false;
              }
              return env;
            });

            this.actions._updateAll(allEnvs);
            resolve(allEnvs);
          }
        });
    });
  };

  this.updatePackagesList = environmentId => {
    // update environment pip list
    this.alt.dispatch(this);

    let envCanUpdate = environmentId => {
      return new Promise((resolve, reject) => {
        this.alt
          .getActions('ApiActions')
          .query()
          .get('/environments/version/' + environmentId)
          .end((err, res) => {
            if (err) {
              reject(err);
            } else if (res.status !== 200) {
              let statusErr = `ERR ${res.status}: ${res.body.message}`;
              reject(statusErr);
            } else {
              resolve(res.body.canUpdate);
            }
          });
      });
    };

    return new Promise((resolve, reject) => {
      let env = this.alt.getStore('EnvironmentStore').getState()
        .environmentCache[environmentId];
      let systemSitePackages =
        env.systemSitePackages !== null ? env.systemSitePackages : true;
      let requestBody = {
        slug: env.slug,
        systemSitePackages: Number(systemSitePackages)
      };
      this.alt
        .getActions('JupyterApiActions')
        .query('pip-freeze', {
          body: JSON.stringify(requestBody),
          method: 'POST'
        })
        .then(data => {
          envCanUpdate(environmentId)
            .then(canUpdate => {
              let allEnvs = this.alt
                .getStore('EnvironmentStore')
                .getState().environments;

              // update package list
              allEnvs = allEnvs.map(env => {
                if (env._id === environmentId) {
                  env.packagesInImage = data?.packages ?? env.packagesInImage;
                  env.canUpdate = canUpdate;
                }
                return env;
              });
              this.actions._updateAll(allEnvs);
              resolve(allEnvs);
            })
            .catch(err => {
              reject(err);
            });
        })
        .catch(err => reject(err));
    });
  };

  // updates the package list in mongo DB.
  // expects object of {slug , packages}
  // only to be called for environemnt with "custom" tag i.e. only for custom environment
  // - called when:
  //    -- all packages for a newly installed env has finished installing
  //    -- new package has been added or removed from package list
  this.updateCustomPackageListInMongoDB = ({ slug, packageList }) => {
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .post('/environments/packages')
        .send({ slug: slug, packages: packageList })
        .end((err, _res) => {
          if (err) {
            console.log(err);
            reject(err);
          } else {
            resolve(true);
          }
        });
    });
  };

  this.acceptAgreement = () => {
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .put('/user/update-intel-terms')
        .end((err, _res) => {
          if (err) {
            reject(err);
          } else {
            resolve(true);
          }
        });
    });
  };

  this.registerInstalled = () => {
    // marks environments as installed if their dirs are present on local filesystem
    this.alt.dispatch(this);

    let getPinned = new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .get('/environments/pinned')
        .end((err, res) => {
          if (err) {
            reject(err);
          } else if (res.status !== 200) {
            let statusErr = `ERR ${res.status}: ${res.body.message}`;
            reject(statusErr);
          } else {
            resolve(res.body);
          }
        });
    });

    return new Promise((resolve, reject) => {
      getPinned
        .then(pinned => {
          // grab list of env dirs on filesystem
          this.alt
            .getActions('JupyterApiActions')
            .query('installed-environments', { method: 'GET' })
            .then(data => {
              const {
                installed,
                active,
                installing,
                quantumJobs,
                quantumJobsEnabled,
                sysPython
              } = data;
              const allEnvs = this.alt
                .getStore('EnvironmentStore')
                .getState().environments;

              if (!installed?.includes(installing)) {
                this.actions._registerInstalling(null);
              }

              const updatedAndFilteredEnvs = allEnvs.reduce((acc, env) => {
                env.installed = installed?.includes(env.slug) ?? false;
                env.active = active?.includes(env.slug) ?? false;
                env.pinned = pinned?.includes(env.slug) ?? false;
                env.quantumJobs = quantumJobs?.includes(env.slug) ?? false;
                env.quantumJobsEnabled =
                  quantumJobsEnabled?.includes(env.slug) ?? false;
                env.sysPython = sysPython?.includes(env.slug) ?? false;

                if (env.slug === installing) {
                  this.actions._registerInstalling(env);
                }

                if (env.installed || !env.isPreInstalled) {
                  acc.push(env);
                }

                return acc;
              }, []);
              this.actions._updateAll(updatedAndFilteredEnvs);
              resolve(updatedAndFilteredEnvs);
            })
            .catch(err => {
              reject(err);
            });
        })
        .catch(err => {
          reject(err);
        });
    });
  };

  this.checkGPU = ({ delayed }) => {
    /* check if GPUs are available on the system
     * @returns
     *   - true: GPU available
     *   - false: GPU not available
     */
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      this.alt
        .getActions('JupyterApiActions')
        .query('gpu-status', { method: 'GET' })
        .then(data => {
          const { gpusAvailable } = data;
          if (delayed) {
            setTimeout(() => {
              resolve(gpusAvailable);
            }, 3000); // a delay of 3 sec has been added only for smooth transition
          } else {
            resolve(gpusAvailable);
          }
        })
        .catch(err => {
          reject(err);
        });
    });
  };

  this.registerInstalling = environmentId => {
    // register environment currently being installed
    this.alt.dispatch(this);

    return new Promise((resolve, _reject) => {
      let installingEnv = this.alt.getStore('EnvironmentStore').getState()
        .environmentCache[environmentId];
      this.actions._registerInstalling(installingEnv);
      resolve(true);
    });
  };

  this.registerInstallingNull = () => {
    // register that no environment is currently being installed
    this.alt.dispatch(this);

    return new Promise((resolve, _reject) => {
      this.actions._registerInstalling(null);
      resolve(true);
    });
  };

  this.createNewEnvironment = envData => {
    // This function uses the new environment information
    // entered by the user to make an API request to create
    // a new environment. On the server side, a new MongoDB
    // document is created, and a clean python virtual
    // environment is copied down into the user's filesystem
    // at /home/jovyan/.qbraid/environments/{slug}. Also
    // inside of that directory a file is created called
    // install_status.txt. This file contains two lines,
    // are updated by the API to indicate if the copying
    // down of the new environment is 'complete' and if
    // it was a 'success'.
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      let formData = new FormData();
      formData.append('name', envData.name);
      formData.append('description', envData.description);
      formData.append('tags', envData.tags);
      formData.append('code', envData.code);
      formData.append('image', envData.image);
      formData.append('kernelName', envData.kernelName);
      formData.append('prompt', envData.prompt);
      formData.append('origin', 'LAB');
      this.alt
        .getActions('ApiActions')
        .query()
        .post('/environments/create')
        .send(formData)
        .end((err, res) => {
          if (err) {
            reject(err);
          } else if (res.status != 200) {
            reject(res.status);
          } else {
            resolve(res.body);
          }
        });
    });
  };

  this.createCustomEnv = envData => {
    this.alt.dispatch(this);

    const { slug, kernelName, prompt, image } = envData;
    const requestBody = { slug, kernelName, prompt, image };

    return new Promise((resolve, reject) => {
      this.alt
        .getActions('JupyterApiActions')
        .query('create-custom-env', {
          body: JSON.stringify(requestBody),
          method: 'POST'
        })
        .then(data => {
          resolve(data.status);
        })
        .catch(err => {
          reject(err);
        });
    });
  };

  this.installPackagesPyvenv = installData => {
    // This function is used to make a call to a JupyterAPI
    // route that will install packages into the new environment.
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      let requestBody = {
        slug: installData.slug,
        packages: installData.packages,
        upgradePip: Number(installData.upgradePip),
        systemSitePackages: Number(installData.systemSitePackages)
      };
      this.alt
        .getActions('JupyterApiActions')
        .query('install-packages', {
          body: JSON.stringify(requestBody),
          method: 'POST'
        })
        .then(data => {
          resolve(data);
        })
        .catch(err => {
          console.log(`ERROR: ${JSON.stringify(err)}`);
          reject(err);
        });
    });
  };

  this.toggleQuantumJobs = ({ slug, action }) => {
    // This function is used to make a call to a JupyterAPI route that
    // will enable/disable qbraid quantum jobs for an environment.
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      const requestBody = {
        slug,
        action // 'enable' or 'disable'
      };
      try {
        this.alt
          .getActions('JupyterApiActions')
          .query('quantum-jobs', {
            body: JSON.stringify(requestBody),
            method: 'PUT'
          })
          .then(data => {
            if (data.success) {
              resolve({ success: data.success, stdout: data.stdout });
            } else {
              reject(new Error(`Action failed with error: ${data.stderr}`));
            }
          })
          .catch(err => {
            const errorMsg = `Error in toggleQuantumJobs: ${err.message}`;
            return reject(errorMsg);
          });
      } catch (err) {
        return reject('Quantum jobs is disabled.');
      }
    });
  };

  this.updateQuantumJobStatus = slug => {
    // This function is used to make a call to a JupyterAPI route that
    // will get qbraid quantum jobs status for an environment.
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      try {
        this.alt
          .getActions('JupyterApiActions')
          .query(`quantum-jobs?slug=${slug}`, { method: 'GET' })
          .then(data => {
            const supported = data?.supported ? Boolean(data.supported) : false;
            const enabled = data?.enabled ? Boolean(data.enabled) : false;
            let allEnvs = this.alt
              .getStore('EnvironmentStore')
              .getState().environments;
            allEnvs = allEnvs.map(env => {
              if (env.slug === slug) {
                env.quantumJobs = supported;
                env.quantumJobsEnabled = enabled;
              }
              return env;
            });
            this.actions._updateAll(allEnvs);
            resolve({ supported, enabled });
          })
          .catch(err => {
            const errorMsg = `Error in getQuantumJobStatus: ${err.message}`;
            return reject(errorMsg);
          });
      } catch (err) {
        return reject('Quantum jobs not added.');
      }
    });
  };

  this.uninstallPackagePyvenv = uninstallData => {
    // This function is used to make a call to a JupyterAPI
    // route that will uninstall a package from an environment.
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      let requestBody = {
        slug: `${uninstallData.slug}`,
        package: `${uninstallData.package}`
      };
      this.alt
        .getActions('JupyterApiActions')
        .query('uninstall-package', {
          body: JSON.stringify(requestBody),
          method: 'POST'
        })
        .then(data => {
          let status = data.status; // 202 or 400
          let message = data.message;
          resolve(status);
        })
        .catch(err => {
          console.log(`Uninstall Error: ${err}`);
          reject(err);
        });
    });
  };

  this.shareEnvironment = shareData => {
    // share environment according to environmentId and collab user email.
    this.alt.dispatch(this);

    return new Promise((resolve, reject) => {
      if (!shareData.environmentId) {
        return reject('Must provide environment id');
      }

      if (!shareData.collabEmail && !shareData.isAccessKeyEnv) {
        return reject('Must provide qBraid collaborator email');
      }

      let env = this.alt.getStore('EnvironmentStore').getState()
        .environmentCache[shareData.environmentId];

      if (!env) {
        return reject('No environment with id ' + environmentId);
      }

      if (!env.slug) {
        return reject('Environment is missing a slug value');
      }

      if (!env.installed) {
        return reject('Environment must be installed to share');
      }

      let requestBody = {
        slug: env.slug,
        collabEmail: shareData?.collabEmail,
        overwrite: shareData?.overwrite || false,
        isAccessKeyEnv: shareData?.isAccessKeyEnv || false
      };

      this.alt
        .getActions('ApiActions')
        .query()
        .post('/environments/share')
        .send(requestBody)
        .end((err, res) => {
          if (err) {
            console.log(err);
            return reject({ status: res.status, message: err });
          } else if (
            res.status !== 200 && // share success
            res.status !== 202 && // share started
            res.status !== 304 // already shared
          ) {
            console.log(
              `Share environment action rejected, status: ${res.status}`
            );
            return reject({
              status: res.status,
              message: JSON.stringify(res.body)
            });
          } else {
            let shareTime = 120;
            if (res.body.hasOwnProperty('shareTime')) {
              shareTime = res.body.shareTime;
            }
            console.log(
              `Share environment action resolved, status: ${res.status}`
            );
            resolve({ status: res.status, shareTime: shareTime });
          }
        });
    });
  };

  this.startInstall = environmentId => {
    // installs the environment with the provided environmentId
    this.alt.dispatch(this);

    return new Promise((resolve, reject) => {
      this.alt
        .getActions('ApiActions')
        .query()
        .post('/environments/install/' + environmentId)
        .end((err, res) => {
          if (err) {
            reject(err);
          } else if (res.status !== 202) {
            reject(res.status);
          } else {
            resolve(res.body.installTime);
          }
        });
    });
  };

  this.pollStatusLocal = () => {
    // poll the install status of installing environment
    this.alt.dispatch(this);

    let env = this.alt
      .getStore('EnvironmentStore')
      .getState().installingEnvironment;

    let api = () => {
      return new Promise((resolve, reject) => {
        this.alt
          .getActions('JupyterApiActions')
          .query(`install-status?slug=${env?.slug}`, { method: 'GET' })
          .then(data => {
            resolve(data);
          })
          .catch(err => {
            console.log(err);
            reject(err);
          });
      });
    };

    return new Promise((resolve, reject) => {
      let count = 0; // current number of polls
      let LIMIT = 100; // maximum number of polls allowed
      let DELAY = 5000; // milisecond delay between polls
      let complete = null; // whether install has reached final state
      let success = null; // whether install was successfull
      let message = null; // message to display to user

      setTimeout(function poll() {
        api()
          .then(data => {
            complete = data?.complete === 1 ? true : false;
            success =
              data?.success === 1
                ? true
                : data?.success === 0
                  ? false
                  : success;
            message = data.message ? data.message : '';
            let seconds = ((count + 1) * DELAY) / 1000;
            if (complete) {
              resolve({ success: success, message: message });
            } else if (++count > LIMIT) {
              reject('Timeout exceeded while polling install status');
            } else {
              setTimeout(poll, DELAY);
            }
          })
          .catch(err => reject(err));
      }, DELAY);
    });
  };

  this.uninstall = slug => {
    // uninstalls the environment with the provided environmentId
    this.alt.dispatch(this);

    let installing = this.alt
      .getStore('EnvironmentStore')
      .getState().installingEnvironment;

    if (installing && slug === installing.slug) {
      this.actions._registerInstalling(null);
    }

    let resetCache = () => {
      this.registerInstalled().catch(err => {
        console.log('Error at RegisterInstalled ', err);
      });
    };

    let removeKernelSpec = new Promise((resolve, reject) => {
      if (!slug) {
        return reject('Must provide the slug of the environment to uninstall');
      }

      let requestBody = { slug: slug };

      this.alt
        .getActions('JupyterApiActions')
        .query('uninstall-environment', {
          body: JSON.stringify(requestBody),
          method: 'POST'
        })
        .then(data => {
          if (this.alt.jupyterlab) {
            let kernelSpecManager =
              this.alt.jupyterlab.serviceManager.kernelspecs;
            kernelSpecManager.refreshSpecs().then(() => {
              if (kernelSpecManager.specs.default) {
                this.alt.jupyterlab.serviceManager.sessions._sessionConnections.forEach(
                  sessionConnection => {
                    try {
                      sessionConnection.changeKernel({
                        name: kernelSpecManager.specs.default
                      });
                    } catch (e) {
                      console.error(e);
                    }
                  }
                );
              }
            });
          }
          resolve(data);
        })
        .catch(err => {
          reject(err);
        });
    });

    return new Promise((resolve, reject) => {
      try {
        removeKernelSpec.then(() => {
          this.updateAll().then(() => {
            this.registerInstalled().then(() => resolve(true));
          });
        });
      } catch (err) {
        console.log(err);
        reject(err);
      }
    });
  };

  this.deleteEnvironment = slug => {
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      try {
        this.alt
          .getActions('ApiActions')
          .query()
          .delete(`/environments/${slug}`)
          .then(res => {
            if (res?.status === 202 || res?.status === 200) {
              resolve(res.message);
            } else {
              reject(res.message);
            }
          })
          .catch(err => {
            reject(err);
          });
      } catch (err) {
        console.log(err);
        reject(err);
      }
    });
  };

  this.generateAccessKey = id => {
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      try {
        this.alt
          .getActions('ApiActions')
          .query()
          .post(`/environments/access-key/${id}`)
          .then(res => {
            if (res?.status === 200) {
              resolve(res);
            } else {
              reject(res.message);
            }
          })
          .catch(err => {
            reject(err);
          });
      } catch (err) {
        console.log(err);
        reject(err);
      }
    });
  };

  this.searchAccessCodeAndAccept = accessKey => {
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      try {
        this.alt
          .getActions('ApiActions')
          .query()
          .put(`/environments/permissions/${accessKey}`)
          .then(res => {
            if (res?.status === 200) {
              resolve(res);
            } else {
              reject(res.message);
            }
          })
          .catch(err => {
            reject(err);
          });
      } catch (err) {
        console.log(err);
        reject(err);
      }
    });
  };

  this.publishEnvironment = slug => {
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      try {
        this.alt
          .getActions('ApiActions')
          .query()
          .post('/environments/publish')
          .send({ slug: slug })
          .then(res => {
            if (res?.status === 200) {
              resolve(res);
            } else {
              reject(res.message);
            }
          })
          .catch(err => {
            reject(err);
          });
      } catch (err) {
        console.log(err);
        reject(err);
      }
    });
  };

  this.updatePublishStatus = (slug, status) => {
    this.alt.dispatch(this);
    return new Promise((resolve, reject) => {
      try {
        this.alt
          .getActions('ApiActions')
          .query()
          .put(`/environments/publish/status/${status}`)
          .send({ slug: slug })
          .then(res => {
            if (res?.status === 200) {
              resolve(res);
            } else {
              reject(res.message);
            }
          })
          .catch(err => {
            reject(err);
          });
      } catch (err) {
        console.log(err);
        reject(err);
      }
    });
  };

  // END ACTION CREATORS
}

export default EnvironmentActions;
