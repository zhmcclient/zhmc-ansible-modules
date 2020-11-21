
:github_url: https://github.com/IBM/ibm_zos_zosmf/tree/master/plugins/modules/zhmc_cpc.py

.. _zhmc_cpc_module:


zhmc_cpc -- Update CPCs
=======================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a CPC (Z system), including its adapters and partitions.
- Update the properties of a CPC.





Parameters
----------


     
hmc_host
  The hostname or IP address of the HMC.


  | **required**: True
  | **type**: str


     
hmc_auth
  The authentication credentials for the HMC, as a dictionary of ``userid``, ``password``.


  | **required**: True
  | **type**: dict


     
  userid
    The userid (username) for authenticating with the HMC.


    | **required**: True
    | **type**: str


     
  password
    The password for authenticating with the HMC.


    | **required**: True
    | **type**: str



     
name
  The name of the target CPC.


  | **required**: True
  | **type**: str


     
state
  The desired state for the attachment:

  * ``set``: Ensures that the CPC has the specified properties.

  * ``facts``: Does not change anything on the CPC and returns the CPC properties including its child resources.


  | **required**: True
  | **type**: str
  | **choices**: set, facts


     
properties
  Only for ``state=set``: New values for the properties of the CPC. Properties omitted in this dictionary will remain unchanged. This parameter will be ignored for ``state=facts``.

  The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for CPC resources, with underscores instead of hyphens. The value of each dictionary item is the property value (in YAML syntax). Integer properties may also be provided as decimal strings.

  The possible properties in this dictionary are the properties defined as writeable in the data model for CPC resources.


  | **required**: False
  | **type**: dict


     
log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  | **required**: False
  | **type**: str


     
faked_session
  A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.


  | **required**: False
  | **type**: raw




Examples
--------

.. code-block:: yaml+jinja

   
   ---
   # Note: The following examples assume that some variables named 'my_*' are set.

   - name: Gather facts about the CPC
     zhmc_cpc:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_cpc_name }}"
       state: facts
     register: cpc1

   - name: Ensure the CPC has the desired property values
     zhmc_cpc:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_cpc_name }}"
       state: set
       properties:
         acceptable_status:
          - active
         description: "This is CPC {{ my_cpc_name }}"











Return Values
-------------


   cpc
        A dictionary with the properties of the CPC, including additional artificial properties as described below.


        | **returned**: success
        | **type**: dict


    name
          CPC name


          | **type**: str



    {property}
          Additional properties of the CPC, as described in the :term:`HMC API` (using hyphens (-) in the property names).


          | **type**: 



    partitions
          Artificial property for the defined partitions of the CPC, with a subset of its properties.


          | **type**: dict


     {name}
            Partition name


            | **type**: dict


      name
              Partition name


              | **type**: str



      status
              Status of the partition


              | **type**: str



      object_uri
              Canonical URI of the partition


              | **type**: str







    adapters
          Artificial property for the adapters of the CPC, with a subset of its properties.


          | **type**: dict


     {name}
            Adapter name


            | **type**: dict


      name
              Adapter name


              | **type**: str



      status
              Status of the adapter


              | **type**: str



      object_uri
              Canonical URI of the adapter


              | **type**: str







    storage-groups
          Artificial property for the storage groups associated with the CPC, with a subset of its properties.


          | **type**: dict


     {name}
            Storage group name


            | **type**: dict


      name
              Storage group name


              | **type**: str



      fulfillment-status
              Fulfillment status of the storage group


              | **type**: str



      object_uri
              Canonical URI of the storage group


              | **type**: str









