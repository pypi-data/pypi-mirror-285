===============
 pubtools-sign
===============

Set of scripts used for signing artifacts via configured signers 


Requirements
============

* Python 3.7+

Features
========
* pubtools-sign
* pubtools-sign-clearsign 
* pubtools-sign-containersign 

Setup
=====

::

  $ pip install -r requirements.txt
  $ pip install . 
  or
  $ python setup.py install

Usage
=====

::

  $ pubtools-sign --help
  $ pubtools-sign-clearsign --help
  $ pubtools-sign-containersign --help

Configuration
=============

Configuration is done via a yaml file. The default location is `~/.config/.pubtools-sign/conf.yaml` or `/etc/pubtools-sign/conf.yaml`. You can also specify a custom location via the `--config` argument. The configuration file is divided into sections, each section is a signer. Each signer has a set of attributes that are used to configure the signer
Conf.yaml has following structure:::

  msg_signer:
    messaging_brokers:
      - <protocol://<host>:<port> for messaging broker
    messaging_cert_key: <path to messaging client key + certificate in PEM format>
    messaging_ca_cert: <path to CA certificate bundle>
    topic_send_to: topic://<topic> - topic where to send signing requests
    topic_listen_to: queue://<queue> - queue where to listen for answers from signing server. Supported templating variables: {creator - UID from client cert}, {task_id}
    environment: <env> - environment attribute which is included in signing request
    service: <service> - service attribute which is included in signing request
    timeout: <int> - timeout for signing request
    retries: <int> - number of retries for receiving signing responses from messaging brokers
    send_retries: <int> - number of retries for whole send + receive cycle
    message_id_key: <id> - attribute in message response used as unique identifier for signing request
    log_level: <level> - log level for pubtools-sign
  cosign_signer:
    rekor_url: <rekor-url>
    upload_tlog: <true|false>
    registry_user: <user> - used to login to registry where images will be signed
    registry_password: <password>
    env_variables:
      <key>: <val> - mapping of environment variables used in signing process. This can be used for example for AWS setup
    key_aliases:
      <alias>: <key> - mapping of key aliases to actual keys. When passing alias as signing key, <key> is used instead. This
                       way you cna define for example "prod-key" alias and have different real keys for different signers
